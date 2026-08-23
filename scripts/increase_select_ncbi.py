#!/usr/bin/env python3
"""Lägg till fler slumpade NCBI-genom utan att röra de som redan valts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from select_ncbi_sample import (
    filter_candidates,
    read_assembly_summary,
    sample_group,
    to_sample_table,
)

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Slumpa fler genom och lägg till i ncbi_sample.tsv"
    )
    p.add_argument(
        "--summary",
        type=Path,
        default=Path("data/meta/assembly_summary_refseq_bacteria_2026-08-21.txt"),
    )
    p.add_argument(
        "--existing",
        type=Path,
        default=Path("config/ncbi_sample.tsv"),
    )
    p.add_argument("--paths", type=Path, default=Path("config/paths.yaml"))
    p.add_argument("--n-complete", type=int, default=20)
    p.add_argument("--n-contig", type=int, default=20)
    p.add_argument("--seed", type=int, default=43)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()

def used_accessions(existing: pd.DataFrame) -> set[str]:
    acc: set[str] = set()
    if "accession" in existing.columns:
        acc |= set(existing["accession"].dropna().str.strip())
    if "sample" in existing.columns:
        acc |= set(existing["sample"].dropna().str.replace("v", ".", regex=False))
    return {a for a in acc if a}

def used_from_raw(data_raw: Path) -> set[str]:
    found: set[str] = set()
    if not data_raw.is_dir():
        return found
    for path in data_raw.iterdir():
        name = path.name
        if "_genomic.fna" in name:
            found.add(name.replace("_genomic.fna", "").replace(".gz", ""))
    return found

def main() -> None:
    args = parse_args()
    if not args.summary.is_file():
        raise SystemExit(f"Hittar inte summary: {args.summary}")
    if not args.existing.is_file():
        raise SystemExit(f"Hittar inte {args.existing} — kör select_ncbi_sample.py först")

    old = pd.read_csv(args.existing, sep="\t", dtype=str)
    used = used_accessions(old)

    if args.paths.is_file():
        cfg = yaml.safe_load(args.paths.read_text(encoding="utf-8"))
        used |= used_from_raw(Path(cfg.get("data_raw", "data/raw")))

    summary = read_assembly_summary(args.summary)
    complete = filter_candidates(summary, "Complete Genome")
    contig = filter_candidates(summary, "Contig")
    complete = complete[~complete["assembly_accession"].isin(used)]
    contig = contig[~contig["assembly_accession"].isin(used)]

    print(f"Redan använda accession: {len(used)}")
    print(f"Kvar complete: {len(complete)}")
    print(f"Kvar contig:   {len(contig)}")
    print(f"Seed: {args.seed}")

    extra_parts = []
    if args.n_complete > 0:
        extra_parts.append(
            to_sample_table(
                sample_group(complete, args.n_complete, args.seed, "complete"),
                "complete",
            )
        )
    if args.n_contig > 0:
        extra_parts.append(
            to_sample_table(
                sample_group(contig, args.n_contig, args.seed, "contig"),
                "contig",
            )
        )
    extra = pd.concat(extra_parts, ignore_index=True) if extra_parts else pd.DataFrame()
    out = pd.concat([old, extra], ignore_index=True)

    print(f"Lägger till {len(extra)} rader (totalt {len(out)})")
    if args.dry_run:
        print(extra.to_string(index=False))
        print("Dry-run: ingen fil skriven")
        return

    out.to_csv(args.existing, sep="\t", index=False)
    print(f"Skrev {args.existing}")

if __name__ == "__main__":
    main()