from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdMolDescriptors
from rdkit.Chem.Scaffolds import MurckoScaffold


FEATURE_COLUMNS = ["canonical_smiles", "scaffold", "hac", "elements", "mw", "logp", "tpsa"]


def _molecule_features(smiles: object) -> dict[str, object] | None:
    if pd.isna(smiles):
        return None
    mol = Chem.MolFromSmiles(str(smiles).strip())
    if mol is None:
        return None
    scaffold = MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False)
    elements = sorted({atom.GetSymbol() for atom in mol.GetAtoms()})
    return {
        "canonical_smiles": Chem.MolToSmiles(mol, canonical=True),
        "scaffold": scaffold or "[acyclic]",
        "hac": int(Lipinski.HeavyAtomCount(mol)),
        "elements": ";".join(elements),
        "mw": float(Descriptors.MolWt(mol)),
        "logp": float(Crippen.MolLogP(mol)),
        "tpsa": float(rdMolDescriptors.CalcTPSA(mol)),
    }


def featurize(frame: pd.DataFrame, smiles_column: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return valid rows with features and rejected rows with a reason."""
    records, rejected = [], []
    for position, (index, value) in enumerate(frame[smiles_column].items()):
        features = _molecule_features(value)
        if features is None:
            rejected.append({"source_index": str(index), "source_position": position, "reason": "invalid_or_missing_smiles"})
        else:
            records.append({"source_index": str(index), "source_position": position, **features})
    feature_frame = pd.DataFrame.from_records(records)
    if feature_frame.empty:
        feature_frame = pd.DataFrame(columns=["source_index", "source_position", *FEATURE_COLUMNS])
    valid = frame.iloc[feature_frame["source_position"].astype(int).tolist()].copy().reset_index(drop=True)
    valid.insert(0, "_molood_row_id", feature_frame["source_position"].astype(int).to_numpy())
    for column in FEATURE_COLUMNS:
        valid[f"_molood_{column}"] = feature_frame[column].to_numpy()
    return valid, pd.DataFrame(rejected, columns=["source_index", "source_position", "reason"])


def dataset_summary(featured: pd.DataFrame, rejected_count: int) -> dict[str, object]:
    n = len(featured)
    scaffolds = featured["_molood_scaffold"] if n else pd.Series(dtype=str)
    element_counts = Counter(e for values in featured.get("_molood_elements", []) for e in str(values).split(";") if e)
    return {
        "valid_molecules": n,
        "rejected_rows": rejected_count,
        "unique_canonical_smiles": int(featured["_molood_canonical_smiles"].nunique()) if n else 0,
        "unique_scaffolds": int(scaffolds.nunique()),
        "largest_scaffold_fraction": float(scaffolds.value_counts(normalize=True).iloc[0]) if n else 0.0,
        "elements": dict(sorted(element_counts.items())),
        "hac_median": float(np.median(featured["_molood_hac"])) if n else None,
    }

