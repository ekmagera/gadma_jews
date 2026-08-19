import ast
import csv
import importlib
import sys
from pathlib import Path

import moments
import yaml


model_name, best_code, sfs_path, scenarios_path, output_path = sys.argv[1:]
parameter_names = {
    "S0": ["nuA", "nuG", "nuM", "T", "mAG", "mAM", "mGM"],
    "T1": ["nuA", "nuG", "nuM", "Tbetween", "Trecent", "mold", "mAG", "mAM", "mGM"],
    "T2": ["nuA", "nuG", "nuM", "Tbetween", "Trecent", "mold", "mAG", "mAM", "mGM"],
    "T3": ["nuA", "nuG", "nuM", "Tbetween", "Trecent", "mold", "mAG", "mAM", "mGM"],
}
module_names = {
    "S0": "S0_simultaneous",
    "T1": "T1_A_GM",
    "T2": "T2_G_AM",
    "T3": "T3_M_AG",
}
if model_name not in parameter_names:
    raise SystemExit(f"Unknown model: {model_name}")

tree = ast.parse(Path(best_code).read_text(encoding="utf-8"))
parameters = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "p0" for target in node.targets):
        parameters = ast.literal_eval(node.value)
        break
if parameters is None:
    raise SystemExit(f"Could not find p0 in {best_code}")

config = yaml.safe_load(Path(scenarios_path).read_text(encoding="utf-8"))
default_length = config.get("sequence_length")
scenarios = config.get("scenarios") or []
if not scenarios:
    raise SystemExit("No scaling scenarios configured")

function = importlib.import_module(module_names[model_name]).model_func
data = moments.Spectrum.from_file(sfs_path)
model = function(parameters, data.sample_sizes)
log_likelihood = float(moments.Inference.ll_multinom(model, data))
theta = float(moments.Inference.optimal_sfs_scaling(model, data))
fitted = dict(zip(parameter_names[model_name], parameters))

rows = []
for scenario in scenarios:
    length = scenario.get("sequence_length", default_length)
    if length is None:
        raise SystemExit(
            "sequence_length is null. Set the callable neutral autosomal length "
            "in config/scaling_scenarios.yaml before scaling."
        )
    mutation_rate = float(scenario["mutation_rate"])
    generation_time = float(scenario["generation_time_years"])
    length = int(length)
    if mutation_rate <= 0 or generation_time <= 0 or length <= 0:
        raise SystemExit(f"Invalid scaling scenario: {scenario}")

    nref = theta / (4.0 * mutation_rate * length)
    row = {
        "scenario": scenario["name"],
        "model": model_name,
        "log_likelihood": log_likelihood,
        "theta": theta,
        "mutation_rate": mutation_rate,
        "sequence_length": length,
        "generation_time_years": generation_time,
        "Nref": nref,
        "NeA": fitted["nuA"] * nref,
        "NeG": fitted["nuG"] * nref,
        "NeM": fitted["nuM"] * nref,
    }
    if model_name == "S0":
        recent_generations = fitted["T"] * 2.0 * nref
        older_generations = recent_generations
    else:
        recent_generations = fitted["Trecent"] * 2.0 * nref
        older_generations = (fitted["Trecent"] + fitted["Tbetween"]) * 2.0 * nref
    row.update({
        "recent_split_generations": recent_generations,
        "older_split_generations": older_generations,
        "recent_split_years": recent_generations * generation_time,
        "older_split_years": older_generations * generation_time,
    })
    for name in ("mold", "mAG", "mAM", "mGM"):
        if name in fitted:
            row[f"{name}_per_generation"] = fitted[name] / (2.0 * nref)
    rows.append(row)

fields = [
    "scenario", "model", "log_likelihood", "theta", "mutation_rate", "sequence_length",
    "generation_time_years", "Nref", "NeA", "NeG", "NeM",
    "recent_split_generations", "older_split_generations",
    "recent_split_years", "older_split_years",
    "mold_per_generation", "mAG_per_generation", "mAM_per_generation", "mGM_per_generation",
]
output = Path(output_path)
output.parent.mkdir(parents=True, exist_ok=True)
with output.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
