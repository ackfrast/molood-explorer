#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
bash scripts/install-local.sh
printf '\nInstallation completed. Press Return to close.\n'
read -r _

