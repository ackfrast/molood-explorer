#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
micromamba_bin="${project_dir}/.local-tools/bin/micromamba"
environment_prefix="${project_dir}/.molood-env"
export MAMBA_ROOT_PREFIX="${project_dir}/.local-tools/mamba-root"
requested_port="${1:-8501}"

if [[ ! -x "${micromamba_bin}" || ! -x "${environment_prefix}/bin/python" ]]; then
    echo "MolOOD Explorer is not installed yet. Run: bash scripts/install-local.sh" >&2
    exit 1
fi

cd "${project_dir}"
selected_port="$("${micromamba_bin}" run --prefix "${environment_prefix}" python -c '
import socket, sys
start = int(sys.argv[1])
with socket.socket() as sock:
    try:
        sock.bind(("127.0.0.1", start))
    except OSError:
        sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
' "${requested_port}")"
if [[ "${selected_port}" != "${requested_port}" ]]; then
    echo "Port ${requested_port} is busy; using ${selected_port} instead."
fi
echo "MolOOD Explorer URL: http://127.0.0.1:${selected_port}"
echo "Keep this terminal open. Press Ctrl+C here to stop the app."
exec "${micromamba_bin}" run --prefix "${environment_prefix}" \
    streamlit run app.py --server.address 127.0.0.1 --server.port "${selected_port}"
