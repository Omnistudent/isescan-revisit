#!/usr/bin/env python3
"""Ladda ner FASTA för rader i config/ncbi_sample.tsv.

- Hoppar över filer som redan finns och ser giltiga ut
- Återupptar avbrutna nedladdningar (curl -C -)
- Skriver till .part och byter namn först när klart
- Loggfilen får bara misslyckanden
"""

from __future__ import annotations

import argparse
import gzip
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Ladda ner NCBI-genom från config/ncbi_sample.tsv"
    )
    p.add_argument(
        "--samples",
        type=Path,
        default=Path("config/ncbi_sample.tsv"),
        help="TSV med kolumnerna fasta och ftp_fasta",
    )
    p.add_argument(
        "--outdir",
        type=Path,
        default=Path("data/raw"),
        help="Katalog för nedladdade FASTA (default: data/raw)",
    )
    p.add_argument(
        "--log",
        type=Path,
        default=Path("results/logs/download_failures.log"),
        help="Loggfil — endast misslyckanden",
    )
    p.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Antal försök per fil (default: 3)",
    )
    p.add_argument(
        "--keep-gz",
        action="store_true",
        help="Behåll .gz efter uppackning (default: ta bort)",
    )
    return p.parse_args()

def log_failure(log_path: Path, message: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{stamp}\t{message}\n")

def looks_like_fasta(path: Path) -> bool:
    """Enkel kontroll: filen börjar med '>' efter ev. gzip."""
    try:
        if path.suffix == ".gz" or path.name.endswith(".gz"):
            with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
                first = handle.readline()
        else:
            with path.open("rt", encoding="utf-8", errors="replace") as handle:
                first = handle.readline()
        return first.startswith(">")
    except OSError:
        return False

def curl_download(url: str, dest: Path, retries: int) -> tuple[bool, str]:
    """Ladda ner med curl, återuppta om .part finns. Returnerar (ok, felmeddelande)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")

    for attempt in range(1, retries + 1):
        cmd = [
            "curl",
            "-fL",
            "--retry",
            "2",
            "--retry-delay",
            "2",
            "-C",
            "-",
            "-o",
            str(part),
            url,
        ]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            return False, "curl saknas i PATH"

        if proc.returncode == 0 and part.is_file() and part.stat().st_size > 0:
            part.replace(dest)
            return True, ""

        err = (proc.stderr or proc.stdout or "okänt fel").strip().replace("\n", " ")
        if attempt == retries:
            if part.is_file() and part.stat().st_size == 0:
                part.unlink(missing_ok=True)
            return False, f"curl exit {proc.returncode}: {err[:300]}"

    return False, "oväntat"

def gunzip_to(src_gz: Path, dest_fna: Path) -> tuple[bool, str]:
    tmp = dest_fna.with_suffix(dest_fna.suffix + ".part")
    try:
        with gzip.open(src_gz, "rb") as zin, tmp.open("wb") as zout:
            shutil.copyfileobj(zin, zout)
        if not looks_like_fasta(tmp):
            tmp.unlink(missing_ok=True)
            return False, "uppackad fil ser inte ut som FASTA"
        tmp.replace(dest_fna)
        return True, ""
    except OSError as exc:
        tmp.unlink(missing_ok=True)
        return False, f"gunzip-fel: {exc}"

def main() -> int:
    args = parse_args()

    if not args.samples.is_file():
        print(f"Hittar inte {args.samples}", file=sys.stderr)
        return 1

    df = pd.read_csv(args.samples, sep="\t", dtype=str)
    required = {"fasta", "ftp_fasta"}
    missing = required - set(df.columns)
    if missing:
        print(f"Saknade kolumner i {args.samples}: {sorted(missing)}", file=sys.stderr)
        return 1

    args.outdir.mkdir(parents=True, exist_ok=True)

    ok_n = skip_n = fail_n = 0

    for _, row in df.iterrows():
        fasta_name = str(row["fasta"]).strip()
        url = str(row["ftp_fasta"]).strip()
        sample = str(row.get("sample", fasta_name)).strip()

        if not fasta_name or not url or url.lower() == "nan":
            msg = f"{sample}\tSAKNAR fasta/ftp_fasta"
            print(f"FAIL  {msg}")
            log_failure(args.log, msg)
            fail_n += 1
            continue

        dest_fna = args.outdir / fasta_name
        dest_gz = args.outdir / (fasta_name + ".gz")

        if dest_fna.is_file() and looks_like_fasta(dest_fna):
            print(f"SKIP  {sample}  (finns: {dest_fna.name})")
            skip_n += 1
            continue

        print(f"GET   {sample}")
        print(f"      {url}")

        if not (dest_gz.is_file() and dest_gz.stat().st_size > 0):
            ok, err = curl_download(url, dest_gz, args.retries)
            if not ok:
                msg = f"{sample}\t{url}\t{err}"
                print(f"FAIL  {err}")
                log_failure(args.log, msg)
                fail_n += 1
                continue

        ok, err = gunzip_to(dest_gz, dest_fna)
        if not ok:
            msg = f"{sample}\t{url}\t{err}"
            print(f"FAIL  {err}")
            log_failure(args.log, msg)
            fail_n += 1
            continue

        if not args.keep_gz:
            dest_gz.unlink(missing_ok=True)

        print(f"OK    {dest_fna.name}")
        ok_n += 1

    print()
    print(f"Klart: {ok_n} nya, {skip_n} redan fanns, {fail_n} misslyckades")
    if fail_n:
        print(f"Misslyckanden loggade i: {args.log}")
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())