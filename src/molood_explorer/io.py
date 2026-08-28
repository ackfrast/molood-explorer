from __future__ import annotations

from pathlib import Path
from typing import IO

import pandas as pd


def load_molecules(source: str | Path | IO[bytes], smiles_column: str | None = None) -> pd.DataFrame:
    """Load CSV, TSV, or one-SMILES-per-line TXT without interpreting chemistry."""
    name = str(getattr(source, "name", source)).lower()
    if name.endswith(".csv"):
        return pd.read_csv(source)
    if name.endswith((".tsv", ".tab")):
        return pd.read_csv(source, sep="\t")
    if name.endswith(".txt"):
        # Accept a header/table when tabs exist; otherwise one SMILES per line.
        frame = pd.read_csv(source, sep="\t", header=None, comment="#")
        if frame.shape[1] == 1:
            frame.columns = [smiles_column or "smiles"]
        else:
            frame.columns = [smiles_column or "smiles"] + [f"column_{i}" for i in range(1, frame.shape[1])]
        return frame
    raise ValueError("Supported input formats are .csv, .tsv, .tab, and .txt")


def validate_columns(frame: pd.DataFrame, smiles_column: str, target_column: str | None = None) -> None:
    missing = [c for c in (smiles_column, target_column) if c and c not in frame.columns]
    if missing:
        raise ValueError(f"Missing column(s): {', '.join(missing)}")

