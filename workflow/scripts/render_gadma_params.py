import sys
from pathlib import Path
import yaml

cfg_path, model, sfs, output = sys.argv[1:]
cfg = yaml.safe_load(open(cfg_path, encoding="utf-8"))["gadma"]
models = {
    "S0": ("models/S0_simultaneous.py", "Null"),
    "T1": ("models/T1_A_GM.py", "Null"),
    "T2": ("models/T2_G_AM.py", "Null"),
    "T3": ("models/T3_M_AG.py", "Null"),
}
filename, identifiers = models[model]
lines = [
    f"Input data: {sfs}", f"Output directory: results/gadma/{model}",
    "Engine: moments", f"Custom filename: {filename}",
    f"Parameter identifiers: {identifiers}",
    f"Number of repeats: {cfg['repeats']}", f"Number of processes: {cfg['processes']}",
]
optional = [("Time for generation", "generation_time"), ("Mutation rate", "mutation_rate"), ("Sequence length", "sequence_length")]
for label, key in optional:
    if cfg.get(key) is not None:
        lines.append(f"{label}: {cfg[key]}")
Path(output).parent.mkdir(parents=True, exist_ok=True)
Path(output).write_text("\n".join(lines) + "\n", encoding="utf-8")
