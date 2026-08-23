#!/usr/bin/env python3
"""Skriv FASTA utan contigar kortare än min_bp.

Om alla contigar filtreras bort behålls den längsta, så att nästa steg
inte får en tom fil."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Filtrera korta FASTA-contigar")
    p.add_argument("--in", dest="infile", type=Path, required=True)
    p.add_argument("--out", dest="outfile", type=Path, required=True)
    p.add_argument("--min-bp", type=int, default=500)
    return p.parse_args()


def read_fasta(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    header = None
    chunks: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith(">"):
                if header is not None:
                    records.append((header, "".join(chunks)))
                header = line[1:].strip()
                chunks = []
            else:
                chunks.append(line.strip())
        if header is not None:
            records.append((header, "".join(chunks)))
    return records


def write_fasta(path: Path, records: list[tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for header, seq in records:
            handle.write(f">{header}\n")
            for i in range(0, len(seq), 80):
                handle.write(seq[i : i + 80] + "\n")


def main() -> None:
    args = parse_args()
    records = read_fasta(args.infile)
    kept = [(h, s) for h, s in records if len(s) >= args.min_bp]
    dropped = len(records) - len(kept)
    if not kept and records:
        longest = max(records, key=lambda rec: len(rec[1]))
        kept = [longest]
        print(
            f"VARNING: alla contigar < {args.min_bp} bp; "
            f"behåller längsta ({len(longest[1])} bp)"
        )
    write_fasta(args.outfile, kept)
    print(
        f"{args.infile.name}: {len(records)} contigar -> {len(kept)} "
        f"(min {args.min_bp} bp, hoppade över {dropped})"
    )


if __name__ == "__main__":
    main()
