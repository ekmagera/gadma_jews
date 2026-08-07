#!/usr/bin/env bash
set -euo pipefail
CORES="${1:-4}"
mkdir -p raw results
if [[ ! -s raw/jews.bcf ]]; then
  echo "Не найден raw/jews.bcf. Скопируйте BCF в папку raw/ перед запуском." >&2
  exit 1
fi
docker run --rm -it -v "$PWD:/work" jews-demography:latest \
  snakemake --snakefile workflow/Snakefile --cores "$CORES" --rerun-incomplete
