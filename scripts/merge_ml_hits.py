#!/usr/bin/env python3
"""Merge homology IS calls with CNN intervals.

Homology hits are kept. CNN intervals that do not overlap a homology hit
(>= min-overlap of the shorter span) are added as family=ML."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

CANON = [
    "seqID",
    "family",
    "cluster",
    "isBegin",
    "isEnd",
    "isLen",
    "type",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Slå ihop homology- och CNN-IS")
    p.add_argument("--base", type=Path, required=True, help="ISEScan eller rust-ise TSV")
    p.add_argument("--ml", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--min-overlap", type=float, default=0.5)
    return p.parse_args()


def load_hits(path: Path) -> pd.DataFrame:
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame(columns=CANON)
    df = pd.read_csv(path, sep="\t", dtype=str, low_memory=False)
    lower = {c.lower(): c for c in df.columns}
    for want in ("seqID", "isBegin", "isEnd"):
        if want.lower() in lower and lower[want.lower()] != want:
            df = df.rename(columns={lower[want.lower()]: want})
    for col in ("isBegin", "isEnd"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "seqID" in df.columns:
        df["seqID"] = df["seqID"].astype(str).str.split().str[0]
    return df


def overlaps(a0: float, a1: float, b0: float, b1: float, min_frac: float) -> bool:
    lo = max(a0, b0)
    hi = min(a1, b1)
    if hi < lo:
        return False
    shorter = min(a1 - a0 + 1, b1 - b0 + 1)
    return shorter > 0 and (hi - lo + 1) / shorter >= min_frac


def main() -> None:
    args = parse_args()
    base = load_hits(args.base)
    ml = load_hits(args.ml)
    extra = []
    if not ml.empty and {"seqID", "isBegin", "isEnd"}.issubset(ml.columns):
        for rec in ml.to_dict(orient="records"):
            hit = False
            if not base.empty and {"seqID", "isBegin", "isEnd"}.issubset(base.columns):
                same = base[base["seqID"].astype(str) == str(rec["seqID"])]
                for other in same.itertuples(index=False):
                    if overlaps(
                        float(rec["isBegin"]),
                        float(rec["isEnd"]),
                        float(other.isBegin),
                        float(other.isEnd),
                        args.min_overlap,
                    ):
                        hit = True
                        break
            if not hit:
                extra.append(rec)
    out = pd.concat([base, pd.DataFrame(extra)], ignore_index=True, sort=False)
    if "source" not in out.columns:
        out["source"] = "homology"
        if extra:
            out.loc[len(base) :, "source"] = "ml"
    elif extra:
        out.loc[len(base) :, "source"] = "ml"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, sep="\t", index=False)
    print(
        f"{args.out}: homology={len(base)}  ml_only={len(extra)}  totalt={len(out)}"
    )


if __name__ == "__main__":
    main()
