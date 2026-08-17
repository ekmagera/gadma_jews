import re
import sys
from pathlib import Path


if len(sys.argv) != 2:
    raise SystemExit("usage: detect_autosomes.py OUTPUT")

contig_pattern = re.compile(r"^##contig=<ID=([^,>]+)")
autosomes = {}

for line in sys.stdin:
    match = contig_pattern.match(line)
    if not match:
        continue

    contig = match.group(1)
    canonical = contig[3:] if contig.lower().startswith("chr") else contig
    if canonical.isdigit() and 1 <= int(canonical) <= 22:
        chromosome = int(canonical)
        if chromosome in autosomes:
            raise SystemExit(
                f"duplicate names for autosome {chromosome}: "
                f"{autosomes[chromosome]!r} and {contig!r}"
            )
        autosomes[chromosome] = contig

missing = [str(chromosome) for chromosome in range(1, 23) if chromosome not in autosomes]
if missing:
    raise SystemExit(
        "BCF header does not contain all canonical autosomes; missing: "
        + ", ".join(missing)
    )

output = Path(sys.argv[1])
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    "".join(f"{autosomes[chromosome]}\n" for chromosome in range(1, 23)),
    encoding="utf-8",
)
