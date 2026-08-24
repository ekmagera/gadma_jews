#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash run_docker.sh preview [cores]       Build QC data and easySFS preview
  bash run_docker.sh projections [cores]   Select projections and write a report
  bash run_docker.sh sfs [cores]           Select projections and build SFS
  bash run_docker.sh smoke [cores]         Evaluate all model functions once
  bash run_docker.sh select [cores]        Fit S0/T1/T2/T3 and write AIC report
  bash run_docker.sh report [cores]        Rebuild AIC report from existing logs
  bash run_docker.sh refine [MODEL] [cores]
                                           Refit winner (or explicit S0/T1/T2/T3)
  bash run_docker.sh scale [MODEL] [cores]  Scale refined winner using scenarios
  bash run_docker.sh pack                   Create a genotype-free handoff archive

There is no built-in wall-clock limit. GADMA stops according to its optimization
criteria and the configured number of independent repeats.
EOF
}

command_name="${1:-}"
if [[ -z "$command_name" || "$command_name" == "help" || "$command_name" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$command_name" != "pack" && ! -s raw/jews.bcf ]]; then
  echo "Missing raw/jews.bcf. Copy the input BCF before running the workflow." >&2
  exit 1
fi

run_snakemake() {
  local cores="$1"
  shift
  mkdir -p results
  local docker_command=(docker)
  if ! docker info >/dev/null 2>&1; then
    if command -v sudo >/dev/null 2>&1 && sudo docker info >/dev/null 2>&1; then
      docker_command=(sudo docker)
    else
      echo "Cannot access the Docker daemon. Ask the administrator for Docker access." >&2
      exit 1
    fi
  fi
  "${docker_command[@]}" run --rm -it --user root -v "$PWD:/work" jews-demography:latest \
    snakemake --directory /work --snakefile /work/workflow/Snakefile \
    --cores "$cores" --rerun-incomplete "$@"
}

read_winner() {
  if [[ ! -s results/model_selection/winner.txt ]]; then
    echo "Missing results/model_selection/winner.txt. Run 'select' first." >&2
    exit 1
  fi
  tr -d '[:space:]' < results/model_selection/winner.txt
}

case "$command_name" in
  preview)
    run_snakemake "${2:-8}" --force results/sfs/preview.txt
    ;;
  projections)
    run_snakemake "${2:-1}" --force results/sfs/selected_projections.tsv
    cat results/sfs/selected_projections.tsv
    ;;
  sfs)
    run_snakemake "${2:-8}" --force results/sfs/dadi/A-G-M.sfs
    cat results/sfs/selected_projections.tsv
    ;;
  smoke)
    run_snakemake "${2:-4}" --force results/smoke/model_evaluation.tsv
    ;;
  select)
    run_snakemake "${2:-8}" results/model_selection/aic.tsv
    ;;
  report)
    run_snakemake "${2:-1}" --force results/model_selection/aic.tsv
    ;;
  refine)
    model="${2:-$(read_winner)}"
    case "$model" in S0|T1|T2|T3) ;; *) echo "Unknown model: $model" >&2; exit 1 ;; esac
    run_snakemake "${3:-4}" "results/refinement/$model/GADMA.log"
    ;;
  scale)
    model="${2:-$(read_winner)}"
    case "$model" in S0|T1|T2|T3) ;; *) echo "Unknown model: $model" >&2; exit 1 ;; esac
    run_snakemake "${3:-1}" --force "results/scaling/$model.tsv"
    ;;
  pack)
    timestamp="$(date +%Y%m%d_%H%M%S)"
    archive="handoff_${timestamp}.tar.gz"
    mkdir -p results
    {
      printf 'created_utc\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      printf 'git_commit\t%s\n' "$(git rev-parse HEAD 2>/dev/null || printf unknown)"
      printf 'raw_genotypes_included\tno\n'
    } > results/handoff_manifest.tsv
    candidates=(
      README.md
      docs/HANDOFF_RU.md
      docs/PARAMETERS_RU.md
      config/config.yaml
      config/scaling_scenarios.yaml
      results/handoff_manifest.tsv
      results/qc/metadata_validation.txt
      results/qc/autosome_contigs.txt
      results/qc/autosomes.variant_counts.tsv
      results/qc/unrelated.king.cutoff.in.id
      results/qc/unrelated.king.cutoff.out.id
      results/sfs/populations.tsv
      results/sfs/preview.txt
      results/sfs/selected_projections.txt
      results/sfs/selected_projections.tsv
      results/sfs/dadi/A-G-M.sfs
      results/model_selection
      results/gadma
      results/refinement
      results/scaling
      results/smoke
    )
    files=()
    for path in "${candidates[@]}"; do
      [[ -e "$path" ]] && files+=("$path")
    done
    tar -czf "$archive" "${files[@]}"
    echo "Created $archive (raw BCF, filtered VCF/BCF and PLINK files are excluded)."
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac
