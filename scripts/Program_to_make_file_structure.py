#!/usr/bin/env python3
"""Skapa projektstruktur för ISEScan-revisit."""

from __future__ import annotations

import argparse
from pathlib import Path

FILES: dict[str, str] = {}

FILES["README.md"] = """# ISEScan revisit

Modern omtagning av homology-baserad IS-detektion.

## Data

Rå FASTA ligger i sökvägen som anges i `config/paths.yaml` (`data_raw`).
Lägg till prover i `config/samples.tsv`.

## Kör

    conda env create -f env/environment.yml
    conda activate isescan-revisit
    snakemake -s workflow/Snakefile -c 4

## Anteckningar

Skriv beslut och resultatvägar i `notes/labbok.md`.
Spara inte misslyckade tester där.
"""

FILES[".gitignore"] = """results/isescan/
results/logs/
.snakemake/
__pycache__/
*.fna
*.fa
*.fasta
*.faa
*.gbk
*.gbff
"""

FILES["config/paths.yaml"] = """# Alla sökvägar på ett ställe. Ändra bara här.
data_raw: {data_raw}
results: results
isescan_outdir: results/isescan

# ISEScan-inställningar
nthread: 4
remove_short_is: false
"""

FILES["config/samples.tsv"] = """sample\tfasta
ecoli_k12\tecoli_k12.fna
gammalt_projekt\tmitt_gamla_genom.fna
"""

FILES["env/environment.yml"] = """name: isescan-revisit
channels:
  - conda-forge
  - bioconda
dependencies:
  - python>=3.10
  - isescan
  - snakemake
  - pandas
  - pyyaml
"""

FILES["workflow/Snakefile"] = '''import pandas as pd
from pathlib import Path

configfile: "config/paths.yaml"

samples = pd.read_csv("config/samples.tsv", sep="\\t").set_index("sample")

RAW = Path(config["data_raw"])
OUT = Path(config["isescan_outdir"])

rule all:
    input:
        expand(str(OUT / "{sample}/{sample}.tsv"), sample=samples.index),
        "results/tables/isescan_summary.tsv"

rule isescan:
    input:
        fasta=lambda w: str(RAW / samples.loc[w.sample, "fasta"])
    output:
        tsv=str(OUT / "{sample}/{sample}.tsv"),
        gff=str(OUT / "{sample}/{sample}.gff"),
        summary=str(OUT / "{sample}/{sample}.sum")
    params:
        outdir=lambda w: str(OUT / w.sample),
        nthread=config["nthread"],
        extra="--removeShortIS" if config["remove_short_is"] else ""
    log:
        "results/logs/isescan_{sample}.log"
    shell:
        """
        mkdir -p {params.outdir}
        isescan.py \\
          --seqfile {input.fasta} \\
          --output {params.outdir} \\
          --nthread {params.nthread} \\
          {params.extra} \\
          > {log} 2>&1

        stem=$(basename {input.fasta})
        mv {params.outdir}/${{stem}}.tsv {output.tsv}
        mv {params.outdir}/${{stem}}.gff {output.gff}
        mv {params.outdir}/${{stem}}.sum {output.summary}
        """

rule summarize:
    input:
        expand(str(OUT / "{sample}/{sample}.tsv"), sample=samples.index)
    output:
        "results/tables/isescan_summary.tsv"
    run:
        frames = []
        for path in input:
            sample = Path(path).stem
            df = pd.read_csv(path, sep="\\t")
            df.insert(0, "sample", sample)
            frames.append(df)
        pd.concat(frames, ignore_index=True).to_csv(output[0], sep="\\t", index=False)
'''

FILES["notes/labbok.md"] = """# Labbok — ISEScan revisit

## {today}
Skapade projektstruktur.
Beslut: sökvägar bara i `config/paths.yaml`.
Beslut: behåll partial IS (`remove_short_is: false`).

## YYYY-MM-DD
Prov:
Kommando: snakemake -s workflow/Snakefile -c 4
Resultat:
Anteckning:
"""

FILES["scripts/README.md"] = """# scripts

Lägg små hjälpskript här, t.ex. jämförelse mot gamla BLASTX-resultat.
Kör inte ad-hoc-analyser direkt i Snakefile förrän de är stabila.
"""

PLACEHOLDERS = [
    "results/isescan/.gitkeep",
    "results/tables/.gitkeep",
    "results/logs/.gitkeep",
]

def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        print(f"hoppar över (finns redan): {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"skrev {path}")

def create_project(root: Path, data_raw: Path, force: bool) -> None:
    from datetime import date

    root = root.resolve()
    data_raw = data_raw.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    data_raw.mkdir(parents=True, exist_ok=True)

    context = {
        "data_raw": str(data_raw),
        "today": date.today().isoformat(),
    }
    format_these = {"config/paths.yaml", "notes/labbok.md"}

    for rel, template in FILES.items():
        content = template.format(**context) if rel in format_these else template
        write_file(root / rel, content, force)

    for rel in PLACEHOLDERS:
        write_file(root / rel, "", force)

    print()
    print(f"Projekt skapat i: {root}")
    print(f"Rådata-katalog:   {data_raw}")
    print("Nästa steg:")
    print(f"  1. Lägg FASTA-filer i {data_raw}")
    print("  2. Uppdatera config/samples.tsv")
    print("  3. conda env create -f env/environment.yml")
    print("  4. snakemake -s workflow/Snakefile -c 4")

def parse_args() -> argparse.Namespace:
    home = Path.home()
    parser = argparse.ArgumentParser(
        description="Skapa ISEScan-revisit-projekt med mappar och mallfiler."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd() / "isescan-revisit",
        help="Projektmapp (default: ./isescan-revisit)",
    )
    parser.add_argument(
        "--data-raw",
        type=Path,
        default=home / "data" / "isescan-revisit" / "raw",
        help="Katalog för rå FASTA (default: ~/data/isescan-revisit/raw)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skriv över filer som redan finns",
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()
    create_project(args.root, args.data_raw, args.force)

if __name__ == "__main__":
    main()