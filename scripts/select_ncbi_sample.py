#!/usr/bin/env python3
"""Slumpa complete- och contig-genom från NCBI assembly_summary."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

def read_assembly_summary(path: Path) -> pd.DataFrame:
    header = None
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.lstrip("#").strip()
            if stripped.startswith("assembly_accession"):
                header = stripped.split("\t")

    if header is None:
        raise SystemExit(
            f"Hittade ingen kolumnrad i {path}. "
            f"Kör: head -n 5 {path}"
        )

    df = pd.read_csv(
        path,
        sep="\t",
        comment="#",
        header=None,
        names=header,
        dtype=str,
        low_memory=False,
    )
    return df

def filter_candidates(df: pd.DataFrame, level: str) -> pd.DataFrame:
    out = df.copy()

    if "version_status" in out.columns:
        out = out[out["version_status"].fillna("").str.lower() == "latest"]

    if "genome_rep" in out.columns:
        out = out[out["genome_rep"].fillna("").str.lower() == "full"]

    if "excluded_from_refseq" in out.columns:
        excl = out["excluded_from_refseq"].fillna("").str.strip().str.lower()
        out = out[excl.isin(["", "na"])]

    if "assembly_level" not in out.columns:
        raise SystemExit(
            "Kolumnen assembly_level saknas. "
            f"Tillgängliga kolumner: {list(out.columns)}"
        )

    out = out[
        out["assembly_level"].fillna("").str.strip().str.lower()
        == level.strip().lower()
    ]

    out = out.dropna(subset=["assembly_accession"])
    ftp = out["ftp_path"].fillna("").str.strip()
    out = out[ftp.str.lower() != "na"]
    out = out[ftp != ""]
    out = out[
        ftp.str.startswith("ftp://")
        | ftp.str.startswith("https://")
        | ftp.str.startswith("http://")
    ]
    return out.reset_index(drop=True)

def sample_group(df: pd.DataFrame, n: int, seed: int, label: str) -> pd.DataFrame:
    if len(df) < n:
        raise SystemExit(
            f"För få {label}-genom efter filter: {len(df)} finns, {n} begärdes.\n"
            "Kör diagnostik med value_counts på assembly_level."
        )
    return df.sample(n=n, random_state=seed)

def to_sample_table(df: pd.DataFrame, level_tag: str) -> pd.DataFrame:
    accession = df["assembly_accession"].str.strip()
    sample = accession.str.replace(".", "v", regex=False)
    ftp = df["ftp_path"].str.strip().str.rstrip("/")
    basename = ftp.str.rsplit("/", n=1).str[-1]
    fasta = accession + "_genomic.fna"

    organism = (
        df["organism_name"].str.strip()
        if "organism_name" in df.columns
        else pd.Series([""] * len(df), index=df.index)
    )
    taxid = (
        df["taxid"].str.strip()
        if "taxid" in df.columns
        else pd.Series([""] * len(df), index=df.index)
    )

    out = pd.DataFrame(
        {
            "sample": sample,
            "accession": accession,
            "fasta": fasta,
            "assembly_level": level_tag,
            "organism_name": organism,
            "taxid": taxid,
            "ftp_path": ftp,
            "ftp_fasta": ftp + "/" + basename + "_genomic.fna.gz",
        }
    )
    return out.reset_index(drop=True)

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Skapa config/ncbi_sample.tsv från NCBI assembly_summary."
    )
    p.add_argument(
        "--summary",
        type=Path,
        default=Path("data/meta/assembly_summary_refseq_bacteria_2026-08-21.txt"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("config/ncbi_sample.tsv"),
    )
    p.add_argument("--n-complete", type=int, default=20)
    p.add_argument("--n-contig", type=int, default=20)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()

def main() -> None:
    args = parse_args()
    if not args.summary.is_file():
        raise SystemExit(f"Hittar inte summary-filen: {args.summary}")

    summary = read_assembly_summary(args.summary)
    print(f"Läste {args.summary} ({len(summary)} rader)")

    if "assembly_level" in summary.columns:
        print("assembly_level i filen:")
        print(summary["assembly_level"].value_counts(dropna=False).to_string())
        print()

    complete = filter_candidates(summary, "Complete Genome")
    contig = filter_candidates(summary, "Contig")

    print(f"Kandidater complete: {len(complete)}")
    print(f"Kandidater contig:   {len(contig)}")
    print(f"Seed: {args.seed}")

    chosen = pd.concat(
        [
            to_sample_table(
                sample_group(complete, args.n_complete, args.seed, "complete"),
                "complete",
            ),
            to_sample_table(
                sample_group(contig, args.n_contig, args.seed, "contig"),
                "contig",
            ),
        ],
        ignore_index=True,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    chosen.to_csv(args.out, sep="\t", index=False)

    print(f"Skrev {len(chosen)} rader till {args.out}")
    print(chosen.groupby("assembly_level").size().to_string())

if __name__ == "__main__":
    main()