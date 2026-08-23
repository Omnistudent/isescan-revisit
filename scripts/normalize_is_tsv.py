#!/usr/bin/env python3
"""Normalisera ISEScan- eller rust-ise-TSV till samma kolumnnamn.

Målkolumner (ISEScan-namn): seqID family cluster isBegin isEnd isLen type
Övriga kolumner behålls. Tom indata ger en tom fil med rubrik."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

CANON = ["seqID", "family", "cluster", "isBegin", "isEnd", "isLen", "type"]

ALIASES = {
    "seqID": ("seqID", "seqid", "sequence", "contig"),
    "family": ("family",),
    "cluster": ("cluster", "tier", "group"),
    "isBegin": ("isBegin", "isBegin", "start", "begin"),
    "isEnd": ("isEnd", "isEnd", "end"),
    "isLen": ("isLen", "len4is", "isLen", "length"),
    "type": ("type",),
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Normalisera IS-TSV")
    p.add_argument("--in", dest="infile", type=Path, required=True)
    p.add_argument("--out", dest="outfile", type=Path, required=True)
    return p.parse_args()


def pick(columns: list[str], names: tuple[str, ...]) -> str | None:
    lower = {c.lower(): c for c in columns}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    return None


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for canon, names in ALIASES.items():
        src = pick(list(df.columns), names)
        if src and src != canon:
            rename[src] = canon
    if rename:
        df = df.rename(columns=rename)
    ordered = [c for c in CANON if c in df.columns]
    rest = [c for c in df.columns if c not in ordered]
    return df[ordered + rest]


def main() -> None:
    args = parse_args()
    args.outfile.parent.mkdir(parents=True, exist_ok=True)
    if not args.infile.is_file() or args.infile.stat().st_size == 0:
        pd.DataFrame(columns=CANON).to_csv(args.outfile, sep="\t", index=False)
        return
    df = pd.read_csv(args.infile, sep="\t", dtype=str, low_memory=False)
    if df.empty:
        pd.DataFrame(columns=CANON).to_csv(args.outfile, sep="\t", index=False)
        return
    normalize(df).to_csv(args.outfile, sep="\t", index=False)


if __name__ == "__main__":
    main()
