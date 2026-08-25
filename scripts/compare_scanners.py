#!/usr/bin/env python3
"""Jämför rust-ise och ISEScan per genom (antal och intervallöverlapp)."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Jämför två IS-skannrar")
    p.add_argument("--samples", type=Path, required=True)
    p.add_argument("--isescan-dir", type=Path, required=True)
    p.add_argument("--rustise-dir", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--min-overlap", type=float, default=0.5)
    return p.parse_args()


def load_hits(path: Path) -> pd.DataFrame:
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame(columns=["seqID", "isBegin", "isEnd", "family", "type"])
    df = pd.read_csv(path, sep="\t", dtype=str, low_memory=False)
    if df.empty:
        return df
    lower = {c.lower(): c for c in df.columns}
    rename = {}
    mapping = {
        "seqID": ("seqID", "seqid"),
        "isBegin": ("isBegin", "isBegin"),
        "isEnd": ("isEnd", "isEnd"),
        "family": ("family",),
        "type": ("type",),
    }
    for canon, names in mapping.items():
        src = next((lower[n.lower()] for n in names if n.lower() in lower), None)
        if src and src != canon:
            rename[src] = canon
    df = df.rename(columns=rename)
    for col in ("isBegin", "isEnd"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def intervals_overlap(a0: int, a1: int, b0: int, b1: int, min_frac: float) -> bool:
    lo = max(a0, b0)
    hi = min(a1, b1)
    if hi < lo:
        return False
    overlap = hi - lo + 1
    shorter = min(a1 - a0 + 1, b1 - b0 + 1)
    if shorter <= 0:
        return False
    return (overlap / shorter) >= min_frac


def count_overlap(left: pd.DataFrame, right: pd.DataFrame, min_frac: float) -> int:
    if left.empty or right.empty:
        return 0
    if not {"seqID", "isBegin", "isEnd"}.issubset(left.columns):
        return 0
    if not {"seqID", "isBegin", "isEnd"}.issubset(right.columns):
        return 0
    matched = 0
    used = set()
    for _, a in left.dropna(subset=["isBegin", "isEnd"]).iterrows():
        for j, b in right.dropna(subset=["isBegin", "isEnd"]).iterrows():
            if j in used:
                continue
            if str(a["seqID"]) != str(b["seqID"]):
                continue
            if intervals_overlap(
                int(a["isBegin"]), int(a["isEnd"]),
                int(b["isBegin"]), int(b["isEnd"]),
                min_frac,
            ):
                matched += 1
                used.add(j)
                break
    return matched


def n_type(df: pd.DataFrame, letter: str) -> int:
    if df.empty or "type" not in df.columns:
        return 0
    return int(df["type"].astype(str).str.lower().str.strip().eq(letter).sum())


def main() -> None:
    args = parse_args()
    samples = pd.read_csv(args.samples, sep="\t", dtype=str)
    rows = []
    for rec in samples.to_dict(orient="records"):
        sample = rec["sample"].strip()
        ise = load_hits(args.isescan_dir / sample / f"{sample}.tsv")
        rust = load_hits(args.rustise_dir / sample / f"{sample}.tsv")
        n_overlap = count_overlap(ise, rust, args.min_overlap)
        n_ise = len(ise)
        n_rust = len(rust)
        rows.append(
            {
                "sample": sample,
                "n_isescan": n_ise,
                "n_rustise": n_rust,
                "n_overlap": n_overlap,
                "n_isescan_only": max(n_ise - n_overlap, 0),
                "n_rustise_only": max(n_rust - n_overlap, 0),
                "n_complete_isescan": n_type(ise, "c"),
                "n_complete_rustise": n_type(rust, "c"),
                "n_partial_isescan": n_type(ise, "p"),
                "n_partial_rustise": n_type(rust, "p"),
            }
        )
    out = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, sep="\t", index=False)
    print(f"Skrev {len(out)} rader till {args.out}")


if __name__ == "__main__":
    main()
