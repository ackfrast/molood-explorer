# MolOOD Explorer v0.1.0

First public preview of a local molecular out-of-distribution scenario exploration and splitting tool.

## Highlights

- CSV, TSV, and TXT molecular input with selectable SMILES and optional target columns.
- Random baseline, Bemis–Murcko scaffold, size/HAC, element, and MW/logP/TPSA property shifts.
- Scenario feasibility, data-derived thresholds, expected counts, confounding notes, and OOD calibration guidance.
- Reproducible proper-train, ID-calibration, OOD-calibration, and OOD-test exports with a JSON manifest.
- Streamlit UI and command-line interface.
- Isolated local installation for Windows, macOS, and Linux without requiring an existing Python or Conda installation.

## Installation

Download the archive for your operating system and extract it before installing. Do not run the application from inside the archive.

- **Windows:** double-click `Install-Windows.bat`, then `Run-Windows.bat`.
- **macOS/Linux:** run `bash scripts/install-local.sh`, then `bash scripts/run-local.sh`. The `.command` launchers are also included for desktop use.

The first installation downloads approximately 265 MB and uses approximately 1.8 GB after extraction. Internet access is only required during installation or updates. Molecular data and analysis remain local.

See `LOCAL_INSTALL.md` for troubleshooting and terminal commands.

## Verification

Use `SHA256SUMS.txt` to verify downloaded archives. This release was tested end-to-end on Linux with Python 3.10, RDKit 2025.09.6, Streamlit 1.62.0, and pytest 8.4.2.

