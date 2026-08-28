from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .chemistry import featurize
from .io import validate_columns


@dataclass(frozen=True)
class SplitConfig:
    scenario: str
    threshold: Any = None
    seed: int = 42
    ood_fraction: float = 0.2
    id_calibration_fraction: float = 0.1
    ood_calibration_fraction: float = 0.5


def _threshold_mask(featured: pd.DataFrame, config: SplitConfig, rng: np.random.Generator) -> np.ndarray:
    n = len(featured)
    scenario = config.scenario.lower()
    if scenario == "random":
        count = max(1, min(n - 1, round(n * config.ood_fraction)))
        mask = np.zeros(n, dtype=bool)
        mask[rng.choice(n, count, replace=False)] = True
        return mask
    if scenario == "scaffold":
        held = config.threshold.get("held_out_scaffolds", []) if isinstance(config.threshold, dict) else config.threshold
        return featured["_molood_scaffold"].isin(list(held or [])).to_numpy()
    if scenario == "element":
        element = config.threshold.get("element") if isinstance(config.threshold, dict) else config.threshold
        return featured["_molood_elements"].map(lambda x: element in str(x).split(";")).to_numpy()
    feature = "hac" if scenario in {"size", "hac"} else scenario.split(":", 1)[-1]
    if feature not in {"hac", "mw", "logp", "tpsa"}:
        raise ValueError(f"Unknown scenario: {config.scenario}")
    value = config.threshold.get("value") if isinstance(config.threshold, dict) else config.threshold
    if value is None:
        value = featured[f"_molood_{feature}"].quantile(1 - config.ood_fraction, interpolation="higher")
    return (featured[f"_molood_{feature}"] >= float(value)).to_numpy()


def _take_calibration(indices: np.ndarray, fraction: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    shuffled = rng.permutation(indices)
    if len(indices) < 2 or fraction <= 0:
        return np.array([], dtype=int), shuffled
    count = max(1, min(len(indices) - 1, round(len(indices) * fraction)))
    return shuffled[:count], shuffled[count:]


def create_split(frame: pd.DataFrame, smiles_column: str, config: SplitConfig,
                 target_column: str | None = None) -> dict[str, Any]:
    validate_columns(frame, smiles_column, target_column)
    for name, value in (("ood_fraction", config.ood_fraction), ("id_calibration_fraction", config.id_calibration_fraction),
                        ("ood_calibration_fraction", config.ood_calibration_fraction)):
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")
    featured, rejected = featurize(frame, smiles_column)
    if len(featured) < 4:
        raise ValueError("At least four valid molecules are required")
    rng = np.random.default_rng(config.seed)
    ood_mask = _threshold_mask(featured, config, rng)
    id_idx, ood_idx = np.flatnonzero(~ood_mask), np.flatnonzero(ood_mask)
    if not len(id_idx) or not len(ood_idx):
        raise ValueError("The selected scenario/threshold must produce non-empty ID and OOD groups")
    id_cal, train = _take_calibration(id_idx, config.id_calibration_fraction, rng)
    ood_cal, ood_test = _take_calibration(ood_idx, config.ood_calibration_fraction, rng)
    output_columns = [c for c in frame.columns]
    parts = {
        "proper_train": featured.iloc[train][output_columns].reset_index(drop=True),
        "id_calibration": featured.iloc[id_cal][output_columns].reset_index(drop=True),
        "ood_calibration": featured.iloc[ood_cal][output_columns].reset_index(drop=True),
        "ood_test": featured.iloc[ood_test][output_columns].reset_index(drop=True),
    }
    row_ids = {
        "proper_train": featured.iloc[train]["_molood_row_id"].astype(int).tolist(),
        "id_calibration": featured.iloc[id_cal]["_molood_row_id"].astype(int).tolist(),
        "ood_calibration": featured.iloc[ood_cal]["_molood_row_id"].astype(int).tolist(),
        "ood_test": featured.iloc[ood_test]["_molood_row_id"].astype(int).tolist(),
    }
    manifest = {
        "format_version": 1,
        "tool": "molood-explorer",
        "smiles_column": smiles_column,
        "target_column": target_column,
        "config": asdict(config),
        "input_rows": len(frame),
        "valid_rows": len(featured),
        "rejected_rows": rejected.to_dict(orient="records"),
        "split_counts": {name: len(value) for name, value in parts.items()},
        "source_row_positions": row_ids,
    }
    return {**parts, "manifest": manifest}


def export_split(result: dict[str, Any], output_dir: str | Path) -> list[Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = []
    for name in ("proper_train", "id_calibration", "ood_calibration", "ood_test"):
        path = destination / f"{name}.csv"
        result[name].to_csv(path, index=False)
        paths.append(path)
    manifest_path = destination / "split_manifest.json"
    manifest_path.write_text(json.dumps(result["manifest"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths.append(manifest_path)
    return paths
