#!/usr/bin/env python3
import argparse
import csv
import re
from pathlib import Path


PAIR_RE = re.compile(r"\((\d+),\s*(\d+)\)")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Select easySFS projections from preview output."
    )
    parser.add_argument("preview")
    parser.add_argument("output_txt")
    parser.add_argument("output_tsv")
    parser.add_argument("mode", choices=("auto", "max", "manual"))
    parser.add_argument("fraction", type=float)
    parser.add_argument("populations", help="Comma-separated population codes")
    parser.add_argument("manual", help="Comma-separated manual projections")
    return parser.parse_args()


def read_preview(path, populations):
    values = {population: [] for population in populations}
    current = None
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line in values:
            current = line
            continue
        if current:
            pairs = [
                (int(projection), int(sites))
                for projection, sites in PAIR_RE.findall(line)
            ]
            values[current].extend(pairs)

    missing = [population for population, pairs in values.items() if not pairs]
    if missing:
        raise ValueError(
            "No projection table found in preview for: " + ", ".join(missing)
        )
    return values


def choose(values, populations, mode, fraction, manual):
    if not 0 < fraction <= 1:
        raise ValueError("min_fraction_of_max_sites must be in (0, 1]")
    if mode == "manual" and len(manual) != len(populations):
        raise ValueError("Manual projection count must match population count")

    selected = []
    report = []
    for index, population in enumerate(populations):
        pairs = values[population]
        by_projection = dict(pairs)
        max_sites = max(by_projection.values())
        max_projection = min(
            projection
            for projection, sites in pairs
            if sites == max_sites
        )

        if mode == "auto":
            threshold = fraction * max_sites
            projection = min(
                projection
                for projection, sites in pairs
                if sites >= threshold
            )
            rule = f"smallest projection with >= {fraction:.4g} of maximum sites"
        elif mode == "max":
            projection = max_projection
            rule = "smallest projection at absolute maximum sites"
        else:
            projection = manual[index]
            if projection not in by_projection:
                available = f"{min(by_projection)}-{max(by_projection)}"
                raise ValueError(
                    f"Manual projection {projection} for {population} is absent "
                    f"from preview (available range {available})"
                )
            rule = "manual"

        sites = by_projection[projection]
        selected.append(projection)
        report.append(
            {
                "population": population,
                "selected_projection": projection,
                "segregating_sites": sites,
                "max_projection": max_projection,
                "max_segregating_sites": max_sites,
                "retained_fraction": f"{sites / max_sites:.6f}",
                "selection_rule": rule,
            }
        )
    return selected, report


def main():
    args = parse_args()
    populations = [
        value.strip() for value in args.populations.split(",") if value.strip()
    ]
    manual = [int(value) for value in args.manual.split(",") if value.strip()]
    values = read_preview(args.preview, populations)
    selected, report = choose(
        values, populations, args.mode, args.fraction, manual
    )

    output_txt = Path(args.output_txt)
    output_tsv = Path(args.output_tsv)
    output_txt.parent.mkdir(parents=True, exist_ok=True)
    output_tsv.parent.mkdir(parents=True, exist_ok=True)
    output_txt.write_text(",".join(map(str, selected)) + "\n", encoding="utf-8")
    with output_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=report[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(report)


if __name__ == "__main__":
    main()
