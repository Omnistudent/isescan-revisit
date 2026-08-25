"""Shared DNA-window helpers and a small 1D CNN for IS pattern detection."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

LABELS = ("none", "partial", "complete")
LABEL_TO_ID = {name: i for i, name in enumerate(LABELS)}
BASE_TO_INT = {"A": 0, "C": 1, "G": 2, "T": 3, "a": 0, "c": 1, "g": 2, "t": 3}
COMPLEMENT = str.maketrans("ACGTacgt", "TGCAtgca")


def fasta_id(header: str) -> str:
    return header.split()[0]


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    header = None
    chunks: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith(">"):
                if header is not None:
                    records[fasta_id(header)] = "".join(chunks).upper()
                header = line[1:].strip()
                chunks = []
            else:
                chunks.append(line.strip())
        if header is not None:
            records[fasta_id(header)] = "".join(chunks).upper()
    return records


def reverse_complement(seq: str) -> str:
    return seq.translate(COMPLEMENT)[::-1]


def encode_seq(seq: str, length: int) -> np.ndarray:
    """Pad/trim to length and encode A,C,G,T as 0-3; other bases as 4."""
    if len(seq) < length:
        seq = seq + ("N" * (length - len(seq)))
    else:
        seq = seq[:length]
    arr = np.frombuffer(seq.encode("ascii"), dtype=np.uint8)
    out = np.full(length, 4, dtype=np.uint8)
    mapping = {ord("A"): 0, ord("C"): 1, ord("G"): 2, ord("T"): 3}
    for code, idx in mapping.items():
        out[arr == code] = idx
    return out


def one_hot(batch: np.ndarray | torch.Tensor) -> torch.Tensor:
    """(N, L) uint8 with 0-4 -> (N, 4, L) float. Ambiguous bases become 0.25."""
    if isinstance(batch, np.ndarray):
        x = torch.from_numpy(batch.astype(np.int64, copy=False))
    else:
        x = batch.long()
    n, length = x.shape
    eye = torch.eye(5, dtype=torch.float32, device=x.device)
    # 4th index is N / other
    eye[4] = 0.25
    encoded = eye[x][:, :, :4]
    return encoded.permute(0, 2, 1).contiguous()


def load_is_table(path: Path) -> pd.DataFrame:
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame(columns=["seqID", "isBegin", "isEnd", "type", "family"])
    df = pd.read_csv(path, sep="\t", dtype=str, low_memory=False)
    if df.empty:
        return df
    lower = {c.lower(): c for c in df.columns}
    rename = {}
    for canon, aliases in {
        "seqID": ("seqID", "seqid"),
        "isBegin": ("isBegin", "isBegin"),
        "isEnd": ("isEnd", "isEnd"),
        "type": ("type",),
        "family": ("family",),
    }.items():
        src = next((lower[a.lower()] for a in aliases if a.lower() in lower), None)
        if src and src != canon:
            rename[src] = canon
    df = df.rename(columns=rename)
    if "seqID" in df.columns:
        df["seqID"] = df["seqID"].astype(str).str.split().str[0]
    for col in ("isBegin", "isEnd"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def overlap_frac(win_start: int, win_end: int, is_start: int, is_end: int) -> float:
    lo = max(win_start, is_start)
    hi = min(win_end, is_end)
    if hi < lo:
        return 0.0
    return (hi - lo + 1) / max(win_end - win_start + 1, 1)


def window_label(win_start: int, win_end: int, hits: pd.DataFrame, min_frac: float) -> int:
    """Return 0/1/2 for none/partial/complete. Coordinates are 1-based inclusive."""
    if hits.empty:
        return 0
    best = 0.0
    label = 0
    for row in hits.itertuples(index=False):
        begin = int(getattr(row, 'isBegin', getattr(row, 'isBegin')))
        end = int(getattr(row, 'isEnd', getattr(row, 'isEnd')))
        frac = overlap_frac(win_start, win_end, begin, end)
        if frac < min_frac:
            continue
        kind = str(getattr(row, "type", "p")).lower().strip()
        cand = 2 if kind == "c" else 1
        if frac > best or (frac == best and cand > label):
            best = frac
            label = cand
    return label


class IsWindowCnn(nn.Module):
    """Small RC-augmented 1D CNN. Classes: none, partial, complete."""

    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv1d(4, 32, kernel_size=7, padding=3),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(2),
            nn.Conv1d(64, 128, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.AdaptiveMaxPool1d(1),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.2),
            nn.Linear(128, 3),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


def load_model(path: Path, device: torch.device) -> IsWindowCnn:
    model = IsWindowCnn().to(device)
    state = torch.load(path, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.eval()
    return model


# Names used by the CLI scripts.
encode_seq = encode_seq
load_is_table = load_is_table
one_hot = one_hot
IsWindowCnn = IsWindowCnn
load_model = load_model
