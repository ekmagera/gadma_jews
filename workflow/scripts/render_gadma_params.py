import sys
from pathlib import Path


(
    model,
    sfs,
    output,
    output_directory,
    repeats,
    processes,
    size_lower,
    size_upper,
    time_lower,
    time_upper,
    migration_lower,
    migration_upper,
) = sys.argv[1:]

models = {
    "S0": ("models/S0_simultaneous.py", ["N", "N", "N", "T", "m", "m", "m"]),
    "T1": ("models/T1_A_GM.py", ["N", "N", "N", "T", "T", "m", "m", "m", "m"]),
    "T2": ("models/T2_G_AM.py", ["N", "N", "N", "T", "T", "m", "m", "m", "m"]),
    "T3": ("models/T3_M_AG.py", ["N", "N", "N", "T", "T", "m", "m", "m", "m"]),
}
filename, identifiers = models[model]
bounds = {
    "N": (float(size_lower), float(size_upper)),
    "T": (float(time_lower), float(time_upper)),
    "m": (float(migration_lower), float(migration_upper)),
}
lower = [bounds[identifier][0] for identifier in identifiers]
upper = [bounds[identifier][1] for identifier in identifiers]
lines = [
    f"Input data: {sfs}", f"Output directory: {output_directory}",
    "Engine: moments", f"Custom filename: {filename}",
    f"Lower bound: {lower}", f"Upper bound: {upper}",
    f"Number of repeats: {repeats}", f"Number of processes: {processes}",
]
Path(output).parent.mkdir(parents=True, exist_ok=True)
Path(output).write_text("\n".join(lines) + "\n", encoding="utf-8")
