from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
import pandas as pd

from .chemistry import dataset_summary, featurize
from .io import validate_columns


def _candidate(name: str, meaning: str, feasible: bool, threshold: Any, n: int, ood: int,
               confounding: str, calibration: str, notes: str = "") -> dict[str, Any]:
    return {
        "scenario": name,
        "chemical_meaning": meaning,
        "feasible": bool(feasible),
        "recommended_threshold": threshold,
        "estimated_train_count": int(n - ood),
        "estimated_ood_count": int(ood),
        "estimated_ood_fraction": float(ood / n) if n else 0.0,
        "confounding": confounding,
        "ood_calibration_suitability": calibration,
        "notes": notes,
    }


def explore_scenarios(frame: pd.DataFrame, smiles_column: str, target_column: str | None = None,
                      desired_ood_fraction: float = 0.2) -> dict[str, Any]:
    validate_columns(frame, smiles_column, target_column)
    featured, rejected = featurize(frame, smiles_column)
    n = len(featured)
    if n < 4:
        raise ValueError("At least four valid molecules are required")
    frac = min(max(float(desired_ood_fraction), 0.05), 0.5)
    wanted = max(1, round(n * frac))
    candidates: list[dict[str, Any]] = []
    candidates.append(_candidate(
        "random", "IID reference split; no deliberate chemical shift.", True, frac, n, wanted,
        "Can hide duplicates and analogue leakage; it is not an OOD claim.",
        "No—use ID calibration as the baseline.", "Included as a performance baseline."))

    counts = featured["_molood_scaffold"].value_counts()
    selected, total = [], 0
    for scaffold, count in counts.sort_values(ascending=True).items():
        selected.append(scaffold)
        total += int(count)
        if total >= wanted:
            break
    scaffold_ok = counts.size >= 3 and total < n
    candidates.append(_candidate(
        "scaffold", "Holds out complete Bemis–Murcko scaffold families.", scaffold_ok,
        {"held_out_scaffolds": selected}, n, total if scaffold_ok else 0,
        "Scaffold correlates with size, series, assay batch, and target labels; acyclic molecules share a coarse pseudo-group.",
        "Yes, when enough held-out scaffolds remain for separate calibration and test sets."))

    hac_threshold = float(featured["_molood_hac"].quantile(1 - frac, interpolation="higher"))
    hac_ood = int((featured["_molood_hac"] >= hac_threshold).sum())
    candidates.append(_candidate(
        "size", "Tests extrapolation from smaller to high-heavy-atom-count molecules.",
        0 < hac_ood < n, {"feature": "hac", "operator": ">=", "value": hac_threshold}, n, hac_ood,
        "HAC is correlated with molecular weight, scaffold complexity, solubility, and often potency.",
        "Yes if the high-HAC tail is large and diverse enough; otherwise reserve it for test only."))

    common = {e for values in featured["_molood_elements"] for e in str(values).split(";")}
    element_sets = featured["_molood_elements"].map(lambda x: set(str(x).split(";")))
    element_counts = Counter(e for s in element_sets for e in s)
    eligible = [(e, c) for e, c in element_counts.items() if 1 <= c <= max(wanted * 2, 1) and c < n]
    element, element_ood = min(eligible, key=lambda item: abs(item[1] - wanted)) if eligible else (None, 0)
    candidates.append(_candidate(
        "element", "Holds out molecules containing a selected comparatively uncommon element.", element is not None,
        {"element": element} if element else None, n, element_ood,
        "Element occurrence may identify a single scaffold, salt form, vendor, or assay campaign.",
        "Conditional—appropriate only when the element-defined group contains multiple chemotypes.",
        f"Observed elements: {', '.join(sorted(common))}."))

    for prop, label in (("mw", "molecular weight"), ("logp", "lipophilicity (logP)"), ("tpsa", "polar surface area")):
        threshold = float(featured[f"_molood_{prop}"].quantile(1 - frac, interpolation="higher"))
        count = int((featured[f"_molood_{prop}"] >= threshold).sum())
        candidates.append(_candidate(
            f"property:{prop}", f"Tests extrapolation into the high-{label} tail.", 0 < count < n,
            {"feature": prop, "operator": ">=", "value": threshold}, n, count,
            f"{label.capitalize()} covaries with size, elements, scaffold, and experimental measurability.",
            "Yes if the tail has enough samples and coverage; diagnose label shift separately."))

    target_summary = None
    if target_column:
        target = featured[target_column]
        numeric = pd.to_numeric(target, errors="coerce")
        target_summary = {
            "column": target_column,
            "non_missing": int(target.notna().sum()),
            "numeric": bool(numeric.notna().sum() == target.notna().sum()),
            "unique": int(target.nunique(dropna=True)),
        }
    return {
        "dataset": dataset_summary(featured, len(rejected)),
        "target": target_summary,
        "candidates": candidates,
        "rejected_rows": rejected.to_dict(orient="records"),
        "_featured": featured,
    }

