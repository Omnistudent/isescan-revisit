#!/usr/bin/env python3
"""Train the IS window CNN. Holdout genomes stay in the test split of the npz."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, str(Path(__file__).resolve().parent))
from is_ml_common import IsWindowCnn, LABELS, one_hot  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Träna IS-CNN")
    p.add_argument("--data", type=Path, default=Path("results/ml/windows.npz"))
    p.add_argument("--out", type=Path, default=Path("results/ml/is_cnn.pt"))
    p.add_argument("--epochs", type=int, default=12)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--seed", type=int, default=7)
    return p.parse_args()


class WindowSet(Dataset):
    def __init__(self, x: np.ndarray, y: np.ndarray):
        self.x = x
        self.y = y.astype(np.int64)

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int):
        return self.x[idx], self.y[idx]


def metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    acc = float((y_true == y_pred).mean()) if len(y_true) else 0.0
    is_true = y_true > 0
    is_pred = y_pred > 0
    tp = int(np.logical_and(is_true, is_pred).sum())
    fp = int(np.logical_and(~is_true, is_pred).sum())
    fn = int(np.logical_and(is_true, ~is_pred).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"acc": acc, "is_precision": prec, "is_recall": rec, "is_f1": f1}


def eval_loader(model: nn.Module, loader: DataLoader, device: torch.device) -> dict:
    model.eval()
    ys = []
    ps = []
    with torch.no_grad():
        for xb, yb in loader:
            logits = model(one_hot(xb).to(device))
            pred = logits.argmax(dim=1).cpu().numpy()
            ps.append(pred)
            ys.append(yb.numpy())
    y_true = np.concatenate(ys) if ys else np.array([], dtype=np.int64)
    y_pred = np.concatenate(ps) if ps else np.array([], dtype=np.int64)
    return metrics(y_true, y_pred)


def main() -> None:
    args = parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    blob = np.load(args.data, allow_pickle=True)
    x, y, split = blob["x"], blob["y"], blob["split"]
    train = WindowSet(x[split == "train"], y[split == "train"])
    test = WindowSet(x[split == "test"], y[split == "test"])
    if len(train) == 0:
        raise SystemExit("Tom träningsmängd.")
    counts = np.bincount(train.y, minlength=3).astype(np.float32)
    weights = counts.sum() / np.maximum(counts, 1.0)
    weights = torch.tensor(weights, dtype=torch.float32, device=device)

    train_loader = DataLoader(train, batch_size=args.batch, shuffle=True, drop_last=False)
    test_loader = DataLoader(test, batch_size=args.batch, shuffle=False)
    model = IsWindowCnn().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = nn.CrossEntropyLoss(weight=weights)

    history = []
    best_f1 = -1.0
    best_state = None
    for epoch in range(1, args.epochs + 1):
        model.train()
        running = 0.0
        n = 0
        for xb, yb in train_loader:
            xb_oh = one_hot(xb).to(device)
            yb = yb.long().to(device)
            opt.zero_grad(set_to_none=True)
            loss = loss_fn(model(xb_oh), yb)
            loss.backward()
            opt.step()
            running += float(loss.item()) * len(yb)
            n += len(yb)
        train_m = eval_loader(model, train_loader, device)
        test_m = eval_loader(model, test_loader, device) if len(test) else {}
        row = {
            "epoch": epoch,
            "loss": running / max(n, 1),
            **{f"train_{k}": v for k, v in train_m.items()},
            **{f"test_{k}": v for k, v in test_m.items()},
        }
        history.append(row)
        print(
            f"epoch {epoch:02d}  loss={row['loss']:.4f}  "
            f"train_f1={train_m['is_f1']:.3f}  "
            f"test_f1={test_m.get('is_f1', float('nan')):.3f}  "
            f"test_rec={test_m.get('is_recall', float('nan')):.3f}"
        )
        score = test_m.get("is_f1", train_m["is_f1"])
        if score >= best_f1:
            best_f1 = score
            best_state = {k: v.detach().cpu() for k, v in model.state_dict().items()}

    args.out.parent.mkdir(parents=True, exist_ok=True)
    torch.save(best_state, args.out)
    metrics_path = args.out.with_suffix(".metrics.json")
    metrics_path.write_text(
        json.dumps(
            {
                "labels": LABELS,
                "device": str(device),
                "n_train": int(len(train)),
                "n_test": int(len(test)),
                "best_test_is_f1": best_f1,
                "history": history,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Sparade {args.out}  best_test_is_f1={best_f1:.3f}")


if __name__ == "__main__":
    main()
