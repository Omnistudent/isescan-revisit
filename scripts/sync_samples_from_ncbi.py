#!/usr/bin/env python3
"""Uppdatera config/samples.tsv från config/ncbi_sample.tsv.

Behåller rader som inte kommer från NCBI (MAG, test).
Uppdaterar fasta på NCBI-rader som redan finns.
Lägger till nya NCBI-rader sist.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Synka samples.tsv från ncbi_sample.tsv")
    p.add_argument("--ncbi", type=Path, default=Path("config/ncbi_sample.tsv"))
    p.add_argument("--samples", type=Path, default=Path("config/samples.tsv"))
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    if not args.ncbi.is_file():
        raise SystemExit(f"Hittar inte {args.ncbi}")

    ncbi = pd.read_csv(args.ncbi, sep="\t", dtype=str)
    if "sample" not in ncbi.columns or "fasta" not in ncbi.columns:
        raise SystemExit("ncbi_sample.tsv måste ha sample och fasta")

    want = ["sample", "fasta", "assembly_level", "organism_name", "accession"]
    cols = [c for c in want if c in ncbi.columns]
    incoming = ncbi[cols].copy()
    incoming["source"] = "ncbi"

    if args.samples.is_file():
        old = pd.read_csv(args.samples, sep="\t", dtype=str)
    else:
        old = pd.DataFrame(columns=["sample", "fasta"])

    if "sample" not in old.columns:
        raise SystemExit("samples.tsv måste ha kolumnen sample")

    old_ids = set(old["sample"].dropna().str.strip())
    new = incoming[~incoming["sample"].isin(old_ids)]
    keep = old.copy()

    if "fasta" in keep.columns:
        fasta_map = incoming.set_index("sample")["fasta"].to_dict()
        mask = keep["sample"].isin(fasta_map)
        keep.loc[mask, "fasta"] = keep.loc[mask, "sample"].map(fasta_map)

    out = pd.concat([keep, new], ignore_index=True)

    print(f"Fanns: {len(old)}")
    print(f"Nya NCBI-rader: {len(new)}")
    print(f"Totalt: {len(out)}")

    if args.dry_run:
        print(new.to_string(index=False) if len(new) else "(inga nya)")
        return

    args.samples.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.samples, sep="\t", index=False)
    print(f"Skrev {args.samples}")

if __name__ == "__main__":
    main()