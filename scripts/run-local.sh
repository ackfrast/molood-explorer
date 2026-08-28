#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
micromamba_bin="${project_dir}/.local-tools/bin/micromamba"
environment_prefix="${project_dir}/.molood-env"
export MAMBA_ROOT_PREFIX="${project_dir}/.local-tools/mamba-root"

if [[ ! -x "${micromamba_bin}" || ! -x "${environment_prefix}/bin/python" ]]; then
    echo "MolOOD Explorer is not installed yet. Run: bash scripts/install-local.sh" >&2
    exit 1
fi

cd "${project_dir}"
exec "${micromamba_bin}" run --prefix "${environment_prefix}" \
    streamlit run app.py --server.address 127.0.0.1 --server.port 8501
