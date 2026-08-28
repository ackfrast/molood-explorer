# MolOOD Explorer

MolOOD Explorer inspects molecular tables, recommends plausible out-of-distribution (OOD) scenarios, and creates reproducible train/calibration/test splits. Version 0.1 supports random baseline, Bemis–Murcko scaffold, size/heavy-atom count (HAC), element occurrence, and MW/logP/TPSA property shifts.

This is a scenario-design aid, not proof that a split represents deployment-time OOD. Inspect assay provenance, dates, labels, duplicates, salts, and series membership before drawing scientific conclusions.

## Run on your own computer

Download and extract the project, then follow [LOCAL_INSTALL.md](LOCAL_INSTALL.md). The included installers support Windows 10/11 x64, macOS Intel/Apple Silicon, and Linux x86-64/ARM64. They install an isolated Python/RDKit/Streamlit environment inside the project folder, so normal use is local and does not require a cluster, VPN, SSH tunnel, or an existing Python installation.

GitHub Release users can double-click `Install-Windows.bat` on Windows, or use `Install-macOS-Linux.command` on macOS/Linux. Always extract the archive before installing.

### Local UI address and ports

The launcher binds only to `127.0.0.1`, so the UI is available only on the computer running MolOOD Explorer. It first tries:

```text
http://127.0.0.1:8501
```

If port 8501 is already used by another application or an earlier Streamlit process, the launcher asks the operating system for another available local port. A URL such as the following is normal:

```text
http://127.0.0.1:57050
```

Open the exact URL printed in the PowerShell/terminal window. The number may change on the next launch. Keep that window open while using the UI, and press `Ctrl+C` in it to stop MolOOD Explorer.

## CentOS 7 / PBS environment

Do not install into or run the project from the old base Conda environment. On this CentOS 7 host, its classic solver can spend a long time reading current conda-forge metadata. Use the standalone, statically linked **Micromamba** solver instead; it does not modify base Conda.

Install Micromamba once using the [official installation instructions](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html). The official automatic installer for Linux is:

```bash
"${SHELL}" <(curl -L micro.mamba.pm)
```

Start a new shell (or follow the installer's shell-hook instructions), return to this repository, then run:

```bash
bash scripts/create_environment.sh
```

The script creates or updates only the `molood-explorer` environment, installs this repository in editable mode without letting pip replace compiled packages, and runs pytest plus import/CLI checks. `environment.yml` includes everything needed by both the CLI and UI: Python 3.10, RDKit, pandas, NumPy, scikit-learn, Matplotlib, Plotly, Streamlit, PyArrow, and pytest.

If your cluster already provides `mamba`, the same script uses it automatically. It deliberately does not fall back to classic `conda`; this avoids the metadata stall observed with the installed legacy Conda. Package download and solving should remain a login-node setup task only if permitted by local policy.

Activation is optional. Either use:

```bash
micromamba activate molood-explorer
```

or run commands without changing the current shell:

```bash
micromamba run -n molood-explorer molood --help
micromamba run -n molood-explorer streamlit run app.py
```

If the cluster blocks network access on login nodes, download/install Micromamba and create the environment through the site-approved interactive or build node; no project code change is required.

Private datasets belong under `data/private/`. Everything in that directory except `.gitkeep` is Git-ignored. Do not copy private rows into examples, tests, screenshots, or bug reports.

## Input

CSV and tabular TSV files preserve all columns. A `.txt` file is interpreted as one SMILES per line (or as headerless tab-separated values). Choose one SMILES column and optionally a target column. Invalid or missing SMILES are rejected and recorded in the report/manifest; output CSVs preserve the original columns and source order values, while split row ordering is seeded.

Try the included synthetic data:

```bash
molood explore examples/synthetic_molecules.csv \
  --smiles-column smiles --target-column activity --output scenario_report.json
```

The report includes chemical meaning, feasibility, a data-derived threshold, expected ID/OOD counts, confounding risks, and OOD-calibration suitability for every candidate.

Create a split using a recommended threshold copied from that report:

```bash
molood split examples/synthetic_molecules.csv \
  --smiles-column smiles --target-column activity \
  --scenario size --threshold '{"feature":"hac","operator":">=","value":7}' \
  --seed 42 --ood-fraction 0.2 \
  --id-calibration-fraction 0.1 --ood-calibration-fraction 0.5 \
  --output-dir outputs/example
```

Outputs are `proper_train.csv`, `id_calibration.csv`, `ood_calibration.csv`, `ood_test.csv`, and `split_manifest.json`. Fractions for calibration are conditional: ID calibration is drawn from the ID group, and OOD calibration from the OOD group. Tiny groups may be unsuitable even when a split is mechanically possible.

## Streamlit UI

```bash
micromamba run -n molood-explorer streamlit run app.py
```

The four-step UI uploads data, compares scenario recommendations, configures a split, previews it, and downloads all outputs as a ZIP. Analysis and splitting remain in the importable `molood_explorer` package.

Streamlit prints a URL after startup. For a remote PBS cluster, do not expose the port publicly; bind it locally and use an SSH tunnel according to site policy:

```bash
micromamba run -n molood-explorer streamlit run app.py \
  --server.address 127.0.0.1 --server.port 8501
```

From your workstation, tunnel that port using the cluster's documented SSH route, then open `http://127.0.0.1:8501` locally.

## Tests

Keep login-node checks small:

```bash
micromamba run -n molood-explorer pytest
micromamba run -n molood-explorer python -m molood_explorer.cli --help
```

Submit large/private datasets and extensive profiling as PBS compute jobs. The current implementation computes RDKit descriptors sequentially in memory; it intentionally does not launch multiprocessing from the UI or CLI.

## Scenario interpretation

- **Random** is an IID baseline, not an OOD claim.
- **Scaffold** holds complete Bemis–Murcko families out. Acyclic structures share a coarse `[acyclic]` group.
- **Size/HAC** uses the high-HAC tail and can be strongly entangled with scaffold, MW, and assay behavior.
- **Element** selects molecules containing an uncommon element; check that it does not merely identify one series or batch.
- **Property** uses the high tail of MW, logP, or TPSA; these descriptors covary with one another and with measurability.

For meaningful OOD calibration, the OOD region must contain enough structurally diverse observations to divide into calibration and test subsets. The tool reports suitability guidance but leaves the scientific decision to the user.
