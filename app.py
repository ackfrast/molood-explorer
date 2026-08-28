from __future__ import annotations

import io
import json
import zipfile

import pandas as pd
import plotly.express as px
import streamlit as st

from molood_explorer.analysis import explore_scenarios
from molood_explorer.io import load_molecules
from molood_explorer.splitting import SplitConfig, create_split


st.set_page_config(page_title="MolOOD Explorer", layout="wide")
st.title("MolOOD Explorer")
st.caption("Upload → Explore scenarios → Configure split → Preview/export")

uploaded = st.file_uploader("1 · Upload molecular data", type=["csv", "tsv", "tab", "txt"])
if not uploaded:
    st.info("Upload a CSV/TXT file, or try examples/synthetic_molecules.csv.")
    st.stop()

try:
    frame = load_molecules(uploaded)
except Exception as exc:
    st.error(f"Could not read input: {exc}")
    st.stop()

columns = list(frame.columns)
smiles_column = st.selectbox("SMILES column", columns, index=columns.index("smiles") if "smiles" in columns else 0)
target_choice = st.selectbox("Optional target column", ["(none)", *[c for c in columns if c != smiles_column]])
target_column = None if target_choice == "(none)" else target_choice
ood_fraction = st.slider("Desired OOD fraction", 0.05, 0.50, 0.20, 0.05)

try:
    report = explore_scenarios(frame, smiles_column, target_column, ood_fraction)
except Exception as exc:
    st.error(str(exc))
    st.stop()

st.subheader("2 · Explore scenarios")
summary_cols = st.columns(4)
for box, (label, value) in zip(summary_cols, [
    ("Valid", report["dataset"]["valid_molecules"]),
    ("Rejected", report["dataset"]["rejected_rows"]),
    ("Scaffolds", report["dataset"]["unique_scaffolds"]),
    ("Largest scaffold", f"{report['dataset']['largest_scaffold_fraction']:.0%}"),
]):
    box.metric(label, value)

candidates = pd.DataFrame(report["candidates"])
st.dataframe(candidates.drop(columns=["recommended_threshold"]), width="stretch", hide_index=True)
featured = report["_featured"]
chart = px.histogram(featured, x="_molood_hac", nbins=min(30, max(5, len(featured) // 2)), title="Heavy atom count distribution")
st.plotly_chart(chart, width="stretch")

st.subheader("3 · Configure split")
feasible = [item for item in report["candidates"] if item["feasible"]]
selected_name = st.selectbox("Scenario", [item["scenario"] for item in feasible])
selected = next(item for item in feasible if item["scenario"] == selected_name)
st.write(selected["chemical_meaning"])
st.warning(f"Potential confounding: {selected['confounding']}")
st.caption(f"OOD calibration: {selected['ood_calibration_suitability']}")
default_threshold = json.dumps(selected["recommended_threshold"], ensure_ascii=False)
threshold_text = st.text_input("Threshold (JSON or scalar)", value=default_threshold)
seed = st.number_input("Seed", min_value=0, value=42, step=1)
c1, c2 = st.columns(2)
id_cal_fraction = c1.slider("ID calibration fraction of ID", 0.0, 0.5, 0.1, 0.05)
ood_cal_fraction = c2.slider("OOD calibration fraction of OOD", 0.0, 0.9, 0.5, 0.05)

try:
    threshold = json.loads(threshold_text)
except json.JSONDecodeError:
    threshold = threshold_text

try:
    result = create_split(frame, smiles_column, SplitConfig(
        scenario=selected_name, threshold=threshold, seed=int(seed), ood_fraction=ood_fraction,
        id_calibration_fraction=id_cal_fraction, ood_calibration_fraction=ood_cal_fraction,
    ), target_column)
except Exception as exc:
    st.error(f"Split is not valid: {exc}")
    st.stop()

st.subheader("4 · Preview/export")
counts = result["manifest"]["split_counts"]
st.bar_chart(pd.Series(counts, name="rows"))
preview_name = st.selectbox("Preview", list(counts))
st.dataframe(result[preview_name].head(100), width="stretch", hide_index=True)

archive = io.BytesIO()
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
    for name in counts:
        bundle.writestr(f"{name}.csv", result[name].to_csv(index=False))
    bundle.writestr("split_manifest.json", json.dumps(result["manifest"], indent=2, ensure_ascii=False))
st.download_button("Download split ZIP", archive.getvalue(), "molood_split.zip", "application/zip")
