#!/usr/bin/env bash
set -euo pipefail

version="${1:-0.1.0}"
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="${project_dir}/release-dist"
staging_root="$(mktemp -d "${TMPDIR:-/tmp}/molood-release.XXXXXX")"
package_name="molood-explorer-${version}"
package_dir="${staging_root}/${package_name}"

cleanup() {
    rm -rf "${staging_root}"
}
trap cleanup EXIT

mkdir -p "${package_dir}/data/private" "${output_dir}"
cp -a \
    "${project_dir}/.gitignore" \
    "${project_dir}/README.md" \
    "${project_dir}/LOCAL_INSTALL.md" \
    "${project_dir}/RELEASE_NOTES.md" \
    "${project_dir}/Install-Windows.bat" \
    "${project_dir}/Run-Windows.bat" \
    "${project_dir}/Install-macOS-Linux.command" \
    "${project_dir}/Run-macOS-Linux.command" \
    "${project_dir}/app.py" \
    "${project_dir}/environment.yml" \
    "${project_dir}/pyproject.toml" \
    "${project_dir}/scripts" \
    "${project_dir}/src" \
    "${project_dir}/tests" \
    "${project_dir}/examples" \
    "${package_dir}/"
cp -a "${project_dir}/data/private/.gitkeep" "${package_dir}/data/private/"

find "${package_dir}" -type d -name '__pycache__' -prune -exec rm -rf {} +
find "${package_dir}" -type f -name '*.pyc' -delete

(
    cd "${staging_root}"
    zip -qr "${output_dir}/${package_name}-windows.zip" "${package_name}"
    tar -czf "${output_dir}/${package_name}-macos-linux.tar.gz" "${package_name}"
)

(
    cd "${output_dir}"
    sha256sum "${package_name}-windows.zip" "${package_name}-macos-linux.tar.gz" > SHA256SUMS.txt
)

cp "${project_dir}/RELEASE_NOTES.md" "${output_dir}/RELEASE_NOTES-${version}.md"
echo "Release artifacts created in ${output_dir}:"
find "${output_dir}" -maxdepth 1 -type f -printf '  %f\n' | sort
