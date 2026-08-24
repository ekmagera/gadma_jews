Dockerized GADMA2 workflow for autosomal demographic analysis of three Jewish populations.

Repository: https://github.com/ekmagera/gadma_jews

Requirements: Git and Docker. Do not commit BCF/VCF, PLINK files, individual genotypes, or analysis results.

Prepare the input files:

```bash
cp /path/to/input.bcf raw/jews.bcf
cp metadata/samples_template.csv metadata/samples.csv
```

Edit `metadata/samples.csv` so that it contains the columns `ID,Population`, with IDs matching the BCF. Allowed population labels are `Ashkenazi Jews`, `Georgian Jews`, and `Mountain Jews`.

Build and run:

```bash
docker build --no-cache -t jews-demography:latest .
bash run_docker.sh select 8
```

The workflow automatically performs QC, removes relatives, selects SFS projections, builds the SFS, and compares S0/T1/T2/T3 by AIC. The selected projections are recorded in `results/sfs/selected_projections.tsv`.

The main settings are in `config/config.yaml`. The selection run uses the configured repeats and number of processes; increase them only when additional CPU/RAM and walltime are available. Projection selection is automatic (`auto`, 99% of the maximum segregating sites). Parameter-selection notes are in `docs/PARAMETERS_RU.md`.

After selecting a topology, optional refinement and scaling are available:

```bash
bash run_docker.sh refine
bash run_docker.sh scale
```

Mutation rate, generation time, and callable sequence length affect only the final scaling to years and population sizes; they do not change the SFS, likelihood, AIC, or selected topology.
