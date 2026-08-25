#!/usr/bin/env python3
"""Scan a FASTA with the IS CNN and merge overlapping windows into intervals."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from is_ml_common import (  # noqa: E402
    encode_seq,
    load_model,
    one_hot,
    read_fasta,
    reverse_complement,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CNN-skanna IS-fönster i FASTA")
    p.add_argument("--fasta", type=Path, required=True)
    p.add_argument("--model", type=Path, default=Path("results/ml/is_cnn.pt"))
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--window", type=int, default=1024)
    p.add_argument("--stride", type=int, default=256)
    p.add_argument("--min-prob", type=float, default=0.65)
    p.add_argument("--batch", type=int, default=128)
    return p.parse_args()


def score_windows(
    seq: str,
    model,
    device: torch.device,
    window: int,
    stride: int,
    batch: int,
) -> list[dict]:
    n = len(seq)
    if n == 0:
        return []
    starts = list(range(0, max(n - window, 0) + 1, stride))
    if n < window:
        starts = [0]
    rows = []
    for i in range(0, len(starts), batch):
        chunk = starts[i : i + batch]
        seqs = []
        rcs = []
        for start0 in chunk:
            sub = seq[start0 : start0 + window]
            seqs.append(encode_seq(sub, window))
            rcs.append(encode_seq(reverse_complement(sub), window))
        x = one_hot(np.stack(seqs)).to(device)
        xr = one_hot(np.stack(rcs)).to(device)
        with torch.no_grad():
            prob = 0.5 * (
                torch.softmax(model(x), dim=1) + torch.softmax(model(xr), dim=1)
            )
        prob = prob.cpu().numpy()
        for start0, p in zip(chunk, prob):
            is_prob = float(p[1] + p[2])
            cls = int(p.argmax())
            rows.append(
                {
                    "start0": start0,
                    "end0": min(start0 + window, n),
                    "is_prob": is_prob,
                    "p_partial": float(p[1]),
                    "p_complete": float(p[2]),
                    "cls": cls,
                }
            )
    return rows


def merge_hits(
    windows: list[dict],
    min_prob: float,
    seq_id: str,
    max_span: int = 4000,
) -> list[dict]:
    kept = [w for w in windows if w["is_prob"] >= min_prob and w["cls"] > 0]
    kept.sort(key=lambda w: w["start0"])
    merged: list[dict] = []
    for win in kept:
        start_new = (
            not merged
            or win["start0"] > merged[-1]["isEnd"] - 1
            or win["end0"] - (merged[-1]["isBegin"] - 1) > max_span
        )
        if start_new:
            merged.append(
                {
                    "seqID": seq_id,
                    "isBegin": win["start0"] + 1,
                    "isEnd": win["end0"],
                    "is_prob": win["is_prob"],
                    "p_partial": win["p_partial"],
                    "p_complete": win["p_complete"],
                    "cls": win["cls"],
                }
            )
            continue
        last = merged[-1]
        last["isEnd"] = max(last["isEnd"], win["end0"])
        if win["is_prob"] > last["is_prob"]:
            last["is_prob"] = win["is_prob"]
            last["p_partial"] = win["p_partial"]
            last["p_complete"] = win["p_complete"]
            last["cls"] = win["cls"]
    for rec in merged:
        rec["isLen"] = rec["isEnd"] - rec["isBegin"] + 1
        rec["type"] = "c" if rec["cls"] == 2 else "p"
        rec["family"] = "ML"
        rec["cluster"] = "cnn"
    return merged


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.model, device)
    fasta = read_fasta(args.fasta)
    hits: list[dict] = []
    for seq_id, seq in fasta.items():
        wins = score_windows(seq, model, device, args.window, args.stride, args.batch)
        hits.extend(merge_hits(wins, args.min_prob, seq_id))
    cols = [
        "seqID",
        "family",
        "cluster",
        "isBegin",
        "isEnd",
        "isLen",
        "type",
        "is_prob",
        "p_partial",
        "p_complete",
    ]
    df = pd.DataFrame(hits, columns=cols)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, sep="\t", index=False)
    print(f"{args.fasta.name}: {len(df)} ML-intervall -> {args.out}")


if __name__ == "__main__":
    main()
