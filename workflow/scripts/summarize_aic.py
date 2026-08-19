import csv
import re
import statistics
import sys
from pathlib import Path


root, output_table, output_winner = map(Path, sys.argv[1:])
models = {
    "S0": (7, "simultaneous split"),
    "T1": (9, "A|(G,M)"),
    "T2": (9, "G|(A,M)"),
    "T3": (9, "M|(A,G)"),
}
row_pattern = re.compile(r"^Run\s+(\d+)\s+(-?\d+(?:\.\d+)?)\s+\(")
repeat_pattern = re.compile(r"^Number of repeats:\s*(\d+)")
rows = []

for model, (parameters, topology) in models.items():
    model_dir = root / model
    log_path = model_dir / "GADMA.log"
    text = log_path.read_text(encoding="utf-8", errors="replace")
    likelihood_by_run = {}
    for line in text.splitlines():
        if match := row_pattern.match(line):
            likelihood_by_run[int(match.group(1))] = float(match.group(2))
    if not likelihood_by_run:
        raise SystemExit(f"No likelihood values found in {log_path}")
    likelihoods = list(likelihood_by_run.values())

    configured_repeats = None
    params_path = model_dir / "params_file"
    if params_path.exists():
        for line in params_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if match := repeat_pattern.match(line):
                configured_repeats = int(match.group(1))
                break

    completed_repeats = len(list(model_dir.glob("*/final_best_logLL_model_moments_code.py")))
    log_likelihood = max(likelihoods)
    aic = 2 * parameters - 2 * log_likelihood
    rows.append({
        "model": model,
        "topology": topology,
        "log_likelihood": log_likelihood,
        "median_log_likelihood": statistics.median(likelihoods),
        "log_likelihood_range": max(likelihoods) - min(likelihoods),
        "parameters": parameters,
        "aic": aic,
        "completed_repeats": completed_repeats,
        "configured_repeats": configured_repeats,
        "status": "complete" if configured_repeats == completed_repeats else "incomplete",
        "boundary_warning": "yes" if "hit their bounds" in text else "no",
    })

rows.sort(key=lambda row: row["aic"])
minimum = rows[0]["aic"]
for row in rows:
    row["delta_aic"] = row["aic"] - minimum

output_table.parent.mkdir(parents=True, exist_ok=True)
fields = [
    "model", "topology", "log_likelihood", "median_log_likelihood",
    "log_likelihood_range", "parameters", "aic", "delta_aic",
    "completed_repeats", "configured_repeats", "status", "boundary_warning",
]
with output_table.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

if not all(row["status"] == "complete" for row in rows):
    winner = "INCOMPLETE"
elif any(row["boundary_warning"] == "yes" for row in rows):
    winner = "BOUNDARY_REVIEW"
else:
    winner = rows[0]["model"]
output_winner.write_text(winner + "\n", encoding="utf-8")
