import csv
import sys
from pathlib import Path

metadata, keep, popfile, *pairs = sys.argv[1:]
mapping = dict(p.split("=", 1) for p in pairs)
keep_ids = {line.split()[0] for line in open(keep, encoding="utf-8") if line.strip()}
rows = list(csv.DictReader(open(metadata, newline="", encoding="utf-8")))
selected = [(r["ID"], mapping[r["Population"]]) for r in rows if r["ID"] in keep_ids]
if not selected:
    raise SystemExit("No unrelated samples remain")
Path(popfile).parent.mkdir(parents=True, exist_ok=True)
Path(popfile).write_text("\n".join(f"{sample}\t{pop}" for sample, pop in selected) + "\n")

