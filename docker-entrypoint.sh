#!/usr/bin/env bash
set -euo pipefail
eval "$(micromamba shell hook --shell bash)"
micromamba activate jews-demography
exec "$@"
