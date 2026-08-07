import csv
import subprocess
import sys
from collections import Counter
from pathlib import Path

bcf, metadata, report, *wanted = sys.argv[1:]
rows = list(csv.DictReader(open(metadata, newline="", encoding="utf-8")))
ids = [r["ID"].strip() for r in rows]
folded = [x.casefold() for x in ids]
dups = sorted(k for k, n in Counter(folded).items() if n > 1)
if dups:
    raise SystemExit(f"Duplicate sample IDs (case-insensitive): {', '.join(dups)}")
bad = sorted(set(r["Population"] for r in rows) - set(wanted))
if bad:
    raise SystemExit(f"Unexpected populations in analysis metadata: {bad}")
samples = subprocess.check_output(["bcftools", "query", "-l", bcf], text=True).splitlines()
missing = sorted(set(ids) - set(samples))
if missing:
    raise SystemExit(f"Metadata samples absent from BCF ({len(missing)}): {missing[:20]}")
extra = sorted(set(samples) - set(ids))
counts = Counter(r["Population"] for r in rows)
Path(report).parent.mkdir(parents=True, exist_ok=True)
Path(report).write_text(
    "metadata_samples\t%d\nbcf_samples\t%d\nexcluded_bcf_samples\t%d\n%s\n" % (
        len(ids), len(samples), len(extra),
        "\n".join(f"population_{k}\t{v}" for k, v in sorted(counts.items()))),
    encoding="utf-8",
)

