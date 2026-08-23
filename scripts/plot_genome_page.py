#!/usr/bin/env python3
"""Skriv reports/genomes/<sample>.html från ISEScan-GFF + FASTA."""
from __future__ import annotations

import argparse
import html
from pathlib import Path

import pandas as pd
import yaml

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--sample", required=True)
    p.add_argument("--paths", type=Path, default=Path("config/paths.yaml"))
    p.add_argument("--samples", type=Path, default=Path("config/samples.tsv"))
    p.add_argument("--stats", type=Path, default=Path("results/tables/genome_stats.tsv"))
    p.add_argument("--outdir", type=Path, default=Path("reports/genomes"))
    p.add_argument("--max-contigs", type=int, default=12)
    p.add_argument("--width", type=int, default=900)
    return p.parse_args()

def fasta_lengths(path: Path) -> dict[str, int]:
    lengths: dict[str, int] = {}
    name = None
    n = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith(">"):
                if name is not None:
                    lengths[name] = n
                name = line[1:].split()[0]
                n = 0
            else:
                n += len(line.strip())
        if name is not None:
            lengths[name] = n
    return lengths

def parse_gff(path: Path) -> list[dict]:
    rows = []
    if not path.is_file():
        return rows
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            seqid, _src, ftype, start, end, _score, strand, _phase, attrs = parts[:9]
            info = {}
            for chunk in attrs.split(";"):
                if "=" in chunk:
                    k, v = chunk.split("=", 1)
                    info[k.strip()] = v.strip()
            rows.append({
                "seqid": seqid,
                "ftype": ftype,
                "start": int(float(start)),
                "end": int(float(end)),
                "strand": strand,
                "family": info.get("family", ""),
                "id": info.get("ID", ""),
            })
    return rows

def color_for(feat: dict) -> str:
    if "tir" in feat["ftype"].lower() or feat["ftype"].lower() == "inverted_repeat":
        return "#111827"
    fam = feat["family"]
    palette = {
        "IS3": "#2563eb", "IS481": "#7c3aed", "IS982": "#db2777",
        "IS66": "#059669", "IS110": "#d97706", "IS5": "#0891b2",
    }
    for key, col in palette.items():
        if fam.startswith(key):
            return col
    return "#f59e0b"

def svg_track(seqid: str, length: int, feats: list[dict], width: int) -> str:
    height, pad, inner = 36, 8, width - 16
    bits = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        f'<rect x="8" y="{pad+6}" width="{inner}" height="8" fill="#e5e7eb" rx="2"/>',
    ]
    for feat in feats:
        x = 8 + (feat["start"] - 1) / length * inner
        w = max(1.5, (feat["end"] - feat["start"] + 1) / length * inner)
        tir = "tir" in feat["ftype"].lower()
        y, h = (pad + 10, 6) if tir else (pad, 10)
        title = html.escape(
            f"{feat['ftype']} {feat['family']} {feat['start']}-{feat['end']} {feat['strand']}"
        )
        bits.append(
            f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" '
            f'fill="{color_for(feat)}"><title>{title}</title></rect>'
        )
    bits.append("</svg>")
    return "\n".join(bits)

def page_html(sample: str, meta: dict, blocks: list[str]) -> str:
    org = html.escape(str(meta.get("organism_name") or ""))
    tags = html.escape(str(meta.get("tags") or ""))
    body = "\n".join(blocks) if blocks else "<p>Ingen GFF att rita.</p>"
    return f"""<!DOCTYPE html>
<html lang="sv"><head><meta charset="utf-8"/>
<title>{html.escape(sample)}</title>
<style>
 body {{ font-family: sans-serif; max-width: 960px; margin: 1.5rem auto; }}
 .meta {{ color: #374151; }}
 .contig {{ margin: 1rem 0 1.4rem; }}
 .contig h2 {{ font-size: 0.95rem; margin: 0 0 0.3rem; }}
</style></head><body>
<p><a href="../is_oversikt.html">← översikt</a></p>
<h1>{html.escape(sample)}</h1>
<p class="meta">{org}<br>taggar: {tags}<br>
IS: {meta.get("n_is", "")} &nbsp; andel: {meta.get("pct_genome_is", "")} %</p>
{body}
<p class="meta">Färg = IS-familj, svart = TIR. Mus över block ger detaljer.</p>
</body></html>
"""

def main() -> None:
    args = parse_args()
    cfg = yaml.safe_load(args.paths.read_text(encoding="utf-8"))
    data_raw = Path(cfg["data_raw"])
    isescan_dir = Path(cfg.get("isescan_outdir", "results/isescan"))
    samples = pd.read_csv(args.samples, sep="\t", dtype=str)
    row = samples[samples["sample"] == args.sample]
    if row.empty:
        raise SystemExit(f"sample {args.sample} saknas i {args.samples}")
    fasta = data_raw / row.iloc[0]["fasta"]
    gff = isescan_dir / args.sample / f"{args.sample}.gff"
    meta = {}
    if args.stats.is_file():
        stats = pd.read_csv(args.stats, sep="\t", dtype=str)
        hit = stats[stats["sample"] == args.sample]
        if not hit.empty:
            meta = hit.iloc[0].to_dict()
    lengths = fasta_lengths(fasta) if fasta.is_file() else {}
    by_seq: dict[str, list] = {}
    for feat in parse_gff(gff):
        by_seq.setdefault(feat["seqid"], []).append(feat)
    ordered = sorted(lengths.items(), key=lambda kv: kv[1], reverse=True)[: args.max_contigs]
    blocks = []
    for seqid, length in ordered:
        svg = svg_track(seqid, length, by_seq.get(seqid, []), args.width)
        blocks.append(
            f'<div class="contig"><h2>{html.escape(seqid)} '
            f"({length:,} bp, {len(by_seq.get(seqid, []))} drag)</h2>{svg}</div>"
        )
    args.outdir.mkdir(parents=True, exist_ok=True)
    out = args.outdir / f"{args.sample}.html"
    out.write_text(page_html(args.sample, meta, blocks), encoding="utf-8")
    print(f"Skrev {out}")

if __name__ == "__main__":
    main()