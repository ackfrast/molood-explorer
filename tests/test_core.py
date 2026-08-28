import json

import pandas as pd
import pytest

from molood_explorer.analysis import explore_scenarios
from molood_explorer.splitting import SplitConfig, create_split, export_split


@pytest.fixture
def molecules():
    return pd.DataFrame({
        "smiles": ["CCO", "CCCO", "CCCCO", "c1ccccc1", "Cc1ccccc1", "Oc1ccccc1",
                   "c1ccncc1", "CCc1ccncc1", "c1ccsc1", "Clc1ccccc1", "Brc1ccccc1", "bad"],
        "target": list(range(12)),
    })


def test_explore_reports_all_scenario_families(molecules):
    report = explore_scenarios(molecules, "smiles", "target")
    names = {item["scenario"] for item in report["candidates"]}
    assert {"random", "scaffold", "size", "element", "property:mw", "property:logp", "property:tpsa"} <= names
    assert report["dataset"]["rejected_rows"] == 1
    assert all("confounding" in item for item in report["candidates"])


def test_random_split_is_reproducible_and_disjoint(molecules):
    config = SplitConfig("random", seed=7, ood_fraction=0.35, id_calibration_fraction=0.25)
    first = create_split(molecules, "smiles", config)
    second = create_split(molecules, "smiles", config)
    assert first["manifest"]["source_row_positions"] == second["manifest"]["source_row_positions"]
    groups = [set(x) for x in first["manifest"]["source_row_positions"].values()]
    assert sum(len(x) for x in groups) == len(set().union(*groups)) == 11


def test_size_split_and_export(molecules, tmp_path):
    result = create_split(molecules, "smiles", SplitConfig("size", threshold=7, seed=1))
    paths = export_split(result, tmp_path)
    assert {p.name for p in paths} == {
        "proper_train.csv", "id_calibration.csv", "ood_calibration.csv", "ood_test.csv", "split_manifest.json"
    }
    manifest = json.loads((tmp_path / "split_manifest.json").read_text())
    assert manifest["config"]["scenario"] == "size"


def test_empty_partition_is_rejected(molecules):
    with pytest.raises(ValueError, match="non-empty"):
        create_split(molecules, "smiles", SplitConfig("size", threshold=999))

