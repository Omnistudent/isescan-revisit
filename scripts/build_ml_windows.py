#!/usr/bin/env python3
"""Build labelled DNA windows from FASTA + ISEScan/rust-ise TSVs.

Labels (teacher): none / partial / complete. Hold out one genome for test."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from is_ml_common import (  # noqa: E402
    encode_seq,
    load_is_table,
    read_fasta,
    reverse_complement,
    window_label,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bygg ML-fönster från IS-lärare")
    p.add_argument("--paths", type=Path, default=Path("config/paths.yaml"))
    p.add_argument("--samples", type=Path, default=Path("config/samples_benchmark.tsv"))
    p.add_argument("--teacher-dir", type=Path, default=None)
    p.add_argument("--window", type=int, default=1024)
    p.add_argument("--stride", type=int, default=256)
    p.add_argument("--min-overlap", type=float, default=0.4)
    p.add_argument("--neg-per-pos", type=int, default=4)
    p.add_argument("--holdout", type=str, default="GCF_014335185v1")
    p.add_argument("--out", type=Path, default=Path("results/ml/windows.npz"))
    p.add_argument("--seed", type=int, default=7)
    return p.parse_args()


def teacher_dir(cfg: dict, override: Path | None) -> Path:
    if override is not None:
        return override
    return Path(cfg.get("isescan_outdir", "results/isescan"))


def fasta_path(cfg: dict, rec: dict) -> Path:
    raw = Path(cfg.get("data_raw") or cfg.get("data_raw") or "data/raw")
    fasta = rec.get("fasta") or rec.get("fasta")
    return raw / str(fasta).strip()


def collect_windows(
    fasta: dict[str, str],
    hits: pd.DataFrame,
    sample: str,
    window: int,
    stride: int,
    min_overlap: float,
) -> list[dict]:
    rows: list[dict] = []
    for seq_id, seq in fasta.items():
        contig_hits = (
            hits[hits["seqID"] == seq_id]
            if not hits.empty and "seqID" in hits.columns
            else hits.iloc[0:0]
        )
        n = len(seq)
        if n < window:
            start = 1
            end = n
            label = window_label(start, end, contig_hits, min_overlap)
            rows.append(
                {
                    "sample": sample,
                    "seqID": seq_id,
                    "start": start,
                    "end": end,
                    "label": label,
                    "seq": seq,
                }
            )
            continue
        for start0 in range(0, n - window + 1, stride):
            start = start0 + 1
            end = start0 + window
            label = window_label(start, end, contig_hits, min_overlap)
            rows.append(
                {
                    "sample": sample,
                    "seqID": seq_id,
                    "start": start,
                    "end": end,
                    "label": label,
                    "seq": seq[start0:end],
                }
            )
        # Center a window on each IS so short/partial copies are not missed.
        for rec in contig_hits.itertuples(index=False):
            begin = int(rec.isBegin)
            end = int(rec.isEnd)
            mid = (begin + end) // 2
            start0 = max(0, min(n - window, mid - window // 2 - 1))
            start = start0 + 1
            wend = start0 + window
            label = window_label(start, wend, contig_hits, min_overlap)
            rows.append(
                {
                    "sample": sample,
                    "seqID": seq_id,
                    "start": start,
                    "end": wend,
                    "label": label,
                    "seq": seq[start0:wend],
                }
            )
    return rows


def subsample_negatives(df: pd.DataFrame, neg_per_pos: int, seed: int) -> pd.DataFrame:
    pos = df[df["label"] > 0]
    neg = df[df["label"] == 0]
    if pos.empty or neg.empty:
        return df
    n_keep = min(len(neg), max(len(pos) * neg_per_pos, 1))
    neg = neg.sample(n=n_keep, random_state=seed)
    return pd.concat([pos, neg], ignore_index=True)


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    cfg = yaml.safe_load(args.paths.read_text(encoding="utf-8"))
    samples = pd.read_csv(args.samples, sep="\t", dtype=str)
    tdir = teacher_dir(cfg, args.teacher_dir)

    rows: list[dict] = []
    for rec in samples.to_dict(orient="records"):
        sample = rec["sample"].strip()
        fasta_file = fasta_path(cfg, rec)
        tsv = tdir / sample / f"{sample}.tsv"
        if not fasta_file.is_file():
            print(f"SAKNAR FASTA {sample} -> {fasta_file}")
            continue
        fasta = read_fasta(fasta_file)
        hits = load_is_table(tsv)
        part = collect_windows(
            fasta, hits, sample, args.window, args.stride, args.min_overlap
        )
        print(
            f"{sample}: {len(part)} fönster, "
            f"IS-fönster={sum(r['label'] > 0 for r in part)}, "
            f"lärare={len(hits)} IS"
        )
        rows.extend(part)

    df = pd.DataFrame(rows)
    if df.empty:
        raise SystemExit("Inga fönster. Kör ISEScan/rust-ise först.")
    df = subsample_negatives(df, args.neg_per_pos, args.seed)

    # Reverse-complement every window once (pattern is strand-agnostic).
    rc_rows = []
    for rec in df.to_dict(orient="records"):
        rc = dict(rec)
        rc["seq"] = reverse_complement(rec["seq"])
        rc["rc"] = 1
        rec["rc"] = 0
        rc_rows.append(rc)
    df["rc"] = 0
    df = pd.concat([df, pd.DataFrame(rc_rows)], ignore_index=True)
    df = df.sample(frac=1.0, random_state=args.seed).reset_index(drop=True)

    encoded = np.stack([encode_seq(s, args.window) for s in df["seq"]], axis=0)
    labels = df["label"].to_numpy(dtype=np.int64)
    split = np.where(df["sample"] == args.holdout, "test", "train")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    meta = args.out.with_suffix(".meta.tsv")
    df.drop(columns=["seq"]).to_csv(meta, sep="\t", index=False)
    np.savez_compressed(
        args.out,
        x=encoded,
        y=labels,
        split=np.array(split),
        window=np.array([args.window]),
        holdout=np.array([args.holdout]),
    )
    print(
        f"Skrev {len(df)} fönster till {args.out} "
        f"(train={(split == 'train').sum()}, test={(split == 'test').sum()})"
    )
    print(df["label"].value_counts().sort_index().to_string())
    _ = rng  # keep seed path obvious for later jitter


if __name__ == "__main__":
    main()
