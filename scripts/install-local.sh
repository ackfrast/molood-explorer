#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tools_dir="${project_dir}/.local-tools"
environment_prefix="${project_dir}/.molood-env"
micromamba_bin="${tools_dir}/bin/micromamba"
export MAMBA_ROOT_PREFIX="${tools_dir}/mamba-root"

case "$(uname -s)-$(uname -m)" in
    Linux-x86_64) platform="linux-64" ;;
    Linux-aarch64|Linux-arm64) platform="linux-aarch64" ;;
    Darwin-x86_64) platform="osx-64" ;;
    Darwin-arm64) platform="osx-arm64" ;;
    *) echo "Unsupported platform: $(uname -s) $(uname -m)" >&2; exit 1 ;;
esac

mkdir -p "${tools_dir}" "${project_dir}/outputs"
local_temp="${project_dir}/.local-temp"
mkdir -p "${local_temp}"
export TMPDIR="${local_temp}"
if [[ ! -x "${micromamba_bin}" ]]; then
    echo "Downloading Micromamba for ${platform}..."
    archive="${tools_dir}/micromamba.tar.bz2"
    curl -fL --retry 2 "https://micro.mamba.pm/api/micromamba/${platform}/latest" -o "${archive}"
    tar -xjf "${archive}" -C "${tools_dir}" bin/micromamba
fi

if [[ -x "${environment_prefix}/bin/python" ]]; then
    echo "Updating the local MolOOD environment..."
    "${micromamba_bin}" install --yes --prefix "${environment_prefix}" --file "${project_dir}/environment.yml"
else
    echo "Installing Python, RDKit, Streamlit, and scientific dependencies..."
    "${micromamba_bin}" create --yes --prefix "${environment_prefix}" --file "${project_dir}/environment.yml"
fi

"${micromamba_bin}" run --prefix "${environment_prefix}" \
    python -m pip install --no-deps --editable "${project_dir}"
"${micromamba_bin}" run --prefix "${environment_prefix}" \
    python -c 'import rdkit, streamlit, plotly, molood_explorer; print("Core imports OK")'
"${micromamba_bin}" run --prefix "${environment_prefix}" \
    molood explore "${project_dir}/examples/synthetic_molecules.csv" \
    --smiles-column smiles --target-column activity \
    --output "${local_temp}/scenario_report.json"

echo "Removing downloaded package caches to reduce disk usage..."
"${micromamba_bin}" clean --all --yes || \
    echo "Warning: cache cleanup failed; the app is installed but may use extra disk space." >&2

echo
echo "Installation and smoke test complete. Start MolOOD Explorer with:"
echo "  bash scripts/run-local.sh"
