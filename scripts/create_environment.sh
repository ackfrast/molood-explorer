#!/usr/bin/env bash
set -euo pipefail

environment_name="molood-explorer"

if command -v micromamba >/dev/null 2>&1; then
    environment_tool="micromamba"
elif command -v mamba >/dev/null 2>&1; then
    environment_tool="mamba"
else
    echo "Error: micromamba (recommended) or mamba is required." >&2
    echo "Install micromamba from https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html" >&2
    exit 1
fi

if "${environment_tool}" env list | awk '{print $1}' | grep -Fxq "${environment_name}"; then
    echo "Environment '${environment_name}' already exists; updating it from environment.yml."
    "${environment_tool}" env update --yes --name "${environment_name}" --file environment.yml
else
    "${environment_tool}" env create --yes --name "${environment_name}" --file environment.yml
fi

# Do not let pip replace RDKit or other compiled packages solved by conda-forge.
"${environment_tool}" run --name "${environment_name}" \
    python -m pip install --no-deps --editable .

"${environment_tool}" run --name "${environment_name}" python -m pytest -q
"${environment_tool}" run --name "${environment_name}" molood --help >/dev/null
"${environment_tool}" run --name "${environment_name}" \
    python -c 'import rdkit, streamlit, plotly; print("Environment ready:", "RDKit", rdkit.__version__, "Streamlit", streamlit.__version__, "Plotly", plotly.__version__)'

echo
echo "Environment '${environment_name}' is ready."
echo "Run the UI without activation:"
echo "  ${environment_tool} run -n ${environment_name} streamlit run app.py"
