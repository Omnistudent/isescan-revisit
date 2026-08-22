#!/usr/bin/env python3
"""Bygg results/tables/genome_stats.tsv från FASTA + ISEScan-TSV.

En rad per genom i config/samples.tsv.

Tanken är att den här tabellen är det Quarto-dashboarden läser.
Lägg nya kolumner längst ner i summarize_genome() så bryts inte det som
redan finns.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sammanfatta ISEScan per genom")
    p.add_argument("--paths", type=Path, default=Path("config/paths.yaml"))
    p.add_argument("--samples", type=Path, default=Path("config/samples.tsv"))
    p.add_argument("--out", type=Path, default=Path("results/tables/genome_stats.tsv"))
    return p.parse_args()

def load_paths(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)

def fasta_stats(fasta: Path) -> dict:
    """Längd, antal contigs och N50 från en FASTA."""
    lengths: list[int] = []
    current = 0
    with fasta.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith(">"):
                if current:
                    lengths.append(current)
                    current = 0
            else:
                current += len(line.strip())
        if current:
            lengths.append(current)

    if not lengths:
        return {
            "genome_bp": 0,
            "n_contigs": 0,
            "n50": 0,
            "longest_contig": 0,
        }

    lengths_sorted = sorted(lengths, reverse=True)
    total = sum(lengths_sorted)
    running = 0
    n50 = lengths_sorted[-1]
    for length in lengths_sorted:
        running += length
        if running >= total / 2:
            n50 = length
            break

    return {
        "genome_bp": total,
        "n_contigs": len(lengths_sorted),
        "n50": n50,
        "longest_contig": lengths_sorted[0],
    }

def read_isescan_tsv(path: Path) -> pd.DataFrame:
    """ISEScan-TSV: en rad per predikterat element."""
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t", dtype=str, low_memory=False)

def col(df: pd.DataFrame, *names: str) -> str | None:
    """Hitta första kolumnnamnet som finns (olika ISEScan-versioner)."""
    lower = {c.lower(): c for c in df.columns}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    return None

def summarize_hits(hits: pd.DataFrame) -> dict:
    """Räkna IS-träffar. Utöka här när du vill ha fler mått."""
    empty = {
        "n_is": 0,
        "n_complete": 0,
        "n_partial": 0,
        "is_bp": 0,
        "n_families": 0,
        "top_family": "",
    }
    if hits.empty:
        return empty

    type_col = col(hits, "type")
    family_col = col(hits, "family")
    begin_col = col(hits, "isBegin")
    end_col = col(hits, "isEnd")
    len_col = col(hits, "isLen", "len4is")

    n_is = len(hits)
    n_complete = 0
    n_partial = 0
    if type_col:
        types = hits[type_col].str.lower().str.strip()
        n_complete = int((types == "c").sum())
        n_partial = int((types == "p").sum())

    # Elementlängd: isLen om den finns, annars isEnd-isBegin+1
    if len_col:
        is_bp = pd.to_numeric(hits[len_col], errors="coerce").fillna(0).sum()
    elif begin_col and end_col:
        b = pd.to_numeric(hits[begin_col], errors="coerce")
        e = pd.to_numeric(hits[end_col], errors="coerce")
        is_bp = (e - b + 1).clip(lower=0).fillna(0).sum()
    else:
        is_bp = 0

    top_family = ""
    n_families = 0
    if family_col:
        fam = hits[family_col].fillna("").str.strip()
        fam = fam[fam != ""]
        n_families = int(fam.nunique())
        if len(fam):
            top_family = str(fam.value_counts().index[0])

    return {
        "n_is": n_is,
        "n_complete": n_complete,
        "n_partial": n_partial,
        "is_bp": int(is_bp),
        "n_families": n_families,
        "top_family": top_family,
    }

def summarize_genome(
    sample: str,
    fasta: Path,
    isescan_tsv: Path,
    extra: dict | None = None,
) -> dict:
    """En rad i genome_stats.tsv.

    extra: valfria kolumner från samples.tsv (t.ex. assembly_level).
    """
    row = {"sample": sample}
    if extra:
        row.update(extra)

    row.update(fasta_stats(fasta))
    hits = read_isescan_tsv(isescan_tsv)
    row.update(summarize_hits(hits))

    genome_bp = row["genome_bp"]
    is_bp = row["is_bp"]
    row["pct_genome_is"] = round(100.0 * is_bp / genome_bp, 4) if genome_bp else 0.0
    row["isescan_tsv"] = str(isescan_tsv)
    row["fasta"] = fasta.name
    return row

def main() -> None:
    args = parse_args()
    cfg = load_paths(args.paths)
    data_raw = Path(cfg["data_raw"])
    isescan_dir = Path(cfg.get("isescan_outdir", "results/isescan"))

    samples = pd.read_csv(args.samples, sep="\t", dtype=str)
    if "sample" not in samples.columns or "fasta" not in samples.columns:
        raise SystemExit("samples.tsv måste ha kolumnerna sample och fasta")

    rows = []
    for rec in samples.to_dict(orient="records"):
        sample = rec["sample"].strip()
        fasta = data_raw / rec["fasta"].strip()
        tsv = isescan_dir / sample / f"{sample}.tsv"

        extra = {}
        for key in ("assembly_level", "source", "organism_name", "accession"):
            if key in rec and pd.notna(rec[key]):
                extra[key] = rec[key]

        if not fasta.is_file():
            print(f"SAKNAR FASTA: {sample} -> {fasta}")
            continue
        if not tsv.is_file():
            print(f"SAKNAR ISEScan-TSV: {sample} -> {tsv}")
            continue

        rows.append(summarize_genome(sample, fasta, tsv, extra))
        print(f"OK  {sample}")

    out = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, sep="\t", index=False)
    print(f"Skrev {len(out)} rader till {args.out}")

if __name__ == "__main__":
    main()