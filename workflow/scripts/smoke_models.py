import csv
import math
import sys
from pathlib import Path

import moments

from S0_simultaneous import model_func as s0
from T1_A_GM import model_func as t1
from T2_G_AM import model_func as t2
from T3_M_AG import model_func as t3


sfs_path, output = sys.argv[1:]
data = moments.Spectrum.from_file(sfs_path)
ns = data.sample_sizes
models = {
    "S0": (s0, [1.0, 1.0, 1.0, 0.001, 0.1, 0.1, 0.1]),
    "T1": (t1, [1.0, 1.0, 1.0, 0.0005, 0.001, 0.1, 0.1, 0.1, 0.1]),
    "T2": (t2, [1.0, 1.0, 1.0, 0.0005, 0.001, 0.1, 0.1, 0.1, 0.1]),
    "T3": (t3, [1.0, 1.0, 1.0, 0.0005, 0.001, 0.1, 0.1, 0.1, 0.1]),
}

rows = []
for name, (function, parameters) in models.items():
    model = function(parameters, ns)
    likelihood = float(moments.Inference.ll_multinom(model, data))
    if not math.isfinite(likelihood):
        raise SystemExit(f"Non-finite likelihood for {name}: {likelihood}")
    rows.append({"model": name, "log_likelihood": likelihood, "status": "ok"})

output = Path(output)
output.parent.mkdir(parents=True, exist_ok=True)
with output.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=["model", "log_likelihood", "status"], delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)
