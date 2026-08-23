Skip to main content

    Ctrl+K
    Ctrl+J

Från ~/isescan-revisit:

git status

Lägg bara till det som är text/kod, inte FASTA eller ISEScan-mellanfiler:

git add notes/labbok.md config/samples.tsv config/paths.yaml
git add results/tables/isescan_summary.tsv
git status

Om du ändrat skript:

git add scripts

Kolla att inte data/raw/, results/isescan/ eller .snakemake/ syns som staged.

git commit -m "Körde ISEScan på NCBI-urvalet, uppdaterad summary"
git push

git add -u går bra om .gitignore redan stänger ute data/ och results/isescan/. Kör git status före commit.

my status looks like this:
On branch main
Your branch is up to date with 'origin/main'.
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified: config/paths.yaml
        modified: config/samples.tsv
        modified: notes/labbok.md
        modified: results/tables/isescan_summary.tsv
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        results/tables/.gitkeep
        scripts/download_ncbi_sample.py

Det ser bra ut. Lägg till det här:

git add config/paths.yaml config/samples.tsv notes/labbok.md
git add results/tables/isescan_summary.tsv
git add scripts/download_ncbi_sample.py

Hoppa över results/tables/.gitkeep — tabellen finns redan.

git status
git commit -m "Nedladdning och ISEScan på NCBI-urvalet"
git push

Då har det blivit dags att analysera datan. Det här steget är minst lika stort som själva körningen av isescan. Helst vill jag ha ett snyggt klickbart interface (i html?) med en översikt av analyserade genom, klickbara och med "mouse over"-information med mer data. Genom-storlek, procent av genomet som upptas av IS-element, IS-familjedistribution och distributionen av fragment (hur stor del av genomet är 100%-längd-transposaser? Hur stor del är bara 30% av förväntad längd på transposasen, etc.).
Vad finns det för tillägg, pipelines och etablerade workflows för detta? Helst vill jag arbeta i något "vetenskapligt" som corda eller rstudio, men mer populära/kommerciella lösningar är välkomna också.

Det finns ingen färdig ISEScan-dashboard. ISbrowser/ISsaga hos ISfinder ger cirkelkartor per genom, men de är webbtjänster för deras annotation — inte för dina 40 TSV-filer.⁠Pmc.ncbi.nlm.nih

Det du vill ha är standard exploratory genomics: en sammanfattningstabell + interaktiv HTML. Bygg den själv i Quarto (det du kallade “corda”). Det är den vetenskapliga, versionsbara vägen.
Rekommenderad stack

Quarto dashboard + R (RStudio) + plotly + DT

    En .qmd som läser isescan_summary.tsv + per-genom .tsv
    Statisk HTML: klick, hover, filter — ingen server
    Ligger bra i git och på GitHub Pages
    Dokumentation: quarto.org/docs/dashboards⁠Quarto

Alternativ om du hellre stannar i Python: samma sak med Quarto + plotly + pandas. Shiny/iSEE är överkurs (kräver R-session). Tableau/Power BI funkar men är sämre att publicera med koden.
Vad du måste räkna före gränssnittet

Ett genom = en rad. Det är “vetenskapen”; HTML är bara visningen.

Per genom:

    genome_bp (summa FASTA-längder)
    n_contigs, N50
    n_IS, n_c, n_p
    is_bp = summa (isEnd − isBegin + 1)
    pct_genome_IS = is_bp / genome_bp
    familjefördelning (antal och bp per family)
    fragment: ISEScan har type (c/p) och ORF-koordinater. “30 % av förväntad transposaslängd” kräver en referenslängd per familj (typisk Tpase från ISfinder / ISEScan-klustret). Sen orf_len / typical_tpase_len i fack t.ex. ≥0.9, 0.5–0.9, 0.3–0.5, <0.3.

Utan den tabellen blir hover bara kosmetik.
Hur gränssnittet kan se ut

    Översiktruta: antal genom, median % IS, complete vs contig
    Klickbar tabell (DT): genom, storlek, % IS, n complete/partial — radklick öppnar detalj
    Plotly: % IS mot genomstorlek, färg = assembly_level; hover = art + N50
    Stackad stapel: familjer per genom
    Histogram eller violin: ORF-längd / förväntad längd

Cirkel-karta à la ISbrowser kan vänta; den är per genom och tar mer tid.
Arbetsordning

    Skript som slår ihop alla results/isescan/*/…tsv + FASTA-statistik → results/tables/genome_stats.tsv
    Ett Quarto-dashboard som bara läser den tabellen
    Sen MAG och contig-ände-hypotesen som extra kolumner

Vill du börjar vi med genome_stats.tsv (Python, samma miljö) eller med en minimal Quarto-mall? Statistiken först är rätt — annars har HTML:en inget att visa.
22 sources

Jag kör ju ise-scan och snakescriptet på wsl, men för denna del, med quarto och grafik, misstänker jag att jag måste gå över till windows, eller?

Nej. Quarto behöver inte Windows. WSL räcker.

Tre vettiga upplägg:

1. Allt i Ubuntu (enklast att hålla ihop)
Installera Quarto + R i WSL:

# Quarto: hämta .deb från https://quarto.org/docs/get-started/
sudo apt install r-base

Rendera:

cd ~/isescan-revisit
quarto render reports/is_oversikt.qmd

Öppna HTML:n i Windows-webbläsaren:

\\wsl$\Ubuntu\home\eris\isescan-revisit\reports\is_oversikt.html

2. RStudio/VS Code i Windows, data i WSL
Öppna \\wsl$\Ubuntu\home\eris\isescan-revisit som projekt. Då skriver du Quarto i Windows men läser samma results/tables/. Undvik att kopiera tabellerna fram och tillbaka.

3. Bara titta i Windows
Själva beräkningen av genome_stats.tsv kan ligga kvar i WSL/Python. HTML-filen öppnar du dubbelklick i Chrome oavsett var den skapades.

Grafiken är JavaScript i HTML. Den ritas i webbläsaren, inte i WSL-terminalen.

Rekommendation: räkna statistiken i samma conda-miljö som ISEScan. Sätt upp Quarto i WSL när tabellen finns. Flytta inte hela projektet tillbaka till /mnt/c bara för plotter.

Ok, allt i wsl. Låt oss starta långsamt. Jag installerar med sudo apt install r-base

Bra start. I Ubuntu:

sudo apt update
sudo apt install r-base

Kolla:

R --version

Det räcker för nu. Quarto, plotly och paketen tar vi i nästa steg — först när r-base sitter.

sudo frågar efter ditt Ubuntu-lösenord (det du satte vid WSL-installationen). Det syns inte när du skriver det.

sudo apt ber om password?

Ja. sudo vill ha Ubuntu-lösenordet för användaren eris — samma som när du skapade WSL-kontot.

Inte Windows-lösenordet.

Det syns inte på skärmen medan du skriver. Skriv det och tryck Enter.

Det gick bra, men vad måste jag nu tänka på vad gäller reqirements, config-filer, folderstruktur och min egen dokumentation?

Håll analysen i samma repo, men som ett eget lager. Rör inte ISEScan-körningen.
Mappar

~/isescan-revisit/
  config/           # orörd: paths, samples
  results/tables/   # ISEScan-output + nya genome_stats.tsv
  results/isescan/  # rå .tsv per genom (läses, committas inte)
  reports/          # Quarto .qmd och färdig .html
  scripts/          # Python för statistik; ev. R-hjälp senare
  notes/labbok.md

reports/ är nytt. HTML kan gitignoreras om den är stor; .qmd ska med.
Config

Inga nya YAML behövs än. När statistikskriptet kommer kan det läsa samma config/paths.yaml och config/samples.tsv. Lägg inte R-sökvägar i paths.yaml förrän de används.
Requirements

Håll dem skilda från conda-miljön isescan-revisit (den är för ISEScan).

    System: r-base (klart)
    Senare: Quarto (.deb) + R-paket tidyverse, plotly, DT via install.packages eller en egen conda-env isescan-report med r-base, quarto

Skriv inte in R-paket i env/environment.yml förrän du vet att du vill ha en gemensam miljö. Två miljöer är tydligare: en för att köra ISEScan, en för att titta.
Labboken

Ny rubrik idag, t.ex.:

## 2026-08-22 — analyslager
Beslut: Quarto + R i WSL, inte Windows.
Installerat: r-base via apt.
Nästa: genome_stats.tsv från ISEScan-TSV + FASTA.
Rör inte workflow/Snakefile för det här steget.

Dokumentera beslut, inte varje apt-rad.
Vad du inte gör nu

Inte mixa MAG-logik i Snakefile. Inte committa HTML förrän den är stabil. Inte installera hela tidyverse innan första tabellen finns.

Nästa konkreta steg: ett Python-skript som bygger results/tables/genome_stats.tsv. Quarto väntar tills den filen finns.

Kan du föreslå ett python-script som bygger results/tables/genome_stats.tsv? Det behöver vara pedagogiskt kommenterat och vara lätt att utöka.

Här är ett första statistikskript: en rad per genom, med krokar för familjer och fragment senare. Spara som scripts/build_genome_stats.py.

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

Kör från ~/isescan-revisit:

conda activate isescan-revisit
python scripts/build_genome_stats.py
head results/tables/genome_stats.tsv

pyyaml finns redan i miljön.

Utöka senare: ny funktion, t.ex. fragment_bins(hits), och row.update(...) i summarize_genome. Rör inte FASTA-delen. En extra TSV family_by_genome.tsv kan du lägga till när översikten fungerar.
5 sources

allt såg bra ut. Min git status ser ut så här:
(isescan-revisit) eris@DESKTOP-17ENJH0:~/isescan-revisit$ git status
On branch main
Your branch is up to date with 'origin/main'.
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified: notes/labbok.md
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        results/tables/.gitkeep
        results/tables/genome_stats.tsv
        scripts/build_genome_stats.py

Lägg till skriptet, tabellen och labboken. Hoppa över .gitkeep.

git add notes/labbok.md
git add scripts/build_genome_stats.py
git add results/tables/genome_stats.tsv
git status
git commit -m "Första genome_stats.tsv från ISEScan och FASTA"
git push

Ok, är det dags att bygga sidan med statistik nu?

Ja — men en tunn första sida, inte hela drömgränssnittet. genome_stats.tsv räcker för översikt, hover och klickbar tabell.

Quarto finns inte i apt som färdigt paket. Två vägar:
Snabbast (samma conda)

conda activate isescan-revisit
conda install -c conda-forge plotly

Då kan ett litet Python-skript skriva en HTML du öppnar i Chrome. Inget extra R.
Quarto (det du vill långsiktigt)

    Ladda ner .deb från quarto.org/docs/get-started
    sudo dpkg -i quarto-*.deb
    I R: install.packages(c("plotly", "DT", "readr"))

Börja med Quarto-mallen reports/is_oversikt.qmd när Quarto är installerat:

---
title: "IS-översikt"
format:
  dashboard:
    theme: default
---

```{r}
#| echo: false
library(readr)
library(plotly)
library(DT)

stats <- read_tsv("results/tables/genome_stats.tsv", show_col_types = FALSE)
```

## Rad {height="20%"}

```{r}
#| content: valuebox
#| title: "Genom"
list(value = nrow(stats))
```

```{r}
#| content: valuebox
#| title: "Median % IS"
list(value = round(median(stats$pct_genome_is, na.rm = TRUE), 2))
```

## Rad

```{r}
#| title: "Genomstorlek mot andel IS"
plot_ly(
  stats,
  x = ~genome_bp / 1e6,
  y = ~pct_genome_is,
  color = ~assembly_level,
  text = ~paste(sample, top_family, sep = "<br>"),
  hoverinfo = "text",
  type = "scatter",
  mode = "markers"
) |>
  layout(xaxis = list(title = "Genom (Mbp)"), yaxis = list(title = "% IS"))
```

## Rad

```{r}
#| title: "Klickbar tabell"
datatable(
  stats[, c("sample", "assembly_level", "genome_bp", "n_contigs",
            "n50", "n_is", "n_complete", "n_partial", "pct_genome_is",
            "top_family")],
  options = list(pageLength = 15),
  filter = "top"
)
```

Render:

cd ~/isescan-revisit
quarto render reports/is_oversikt.qmd

Öppna HTML:n via \\wsl$\Ubuntu\home\eris\isescan-revisit\reports\.

Säg till om du vill ha Quarto-installationen steg för steg, eller Python-HTML:en först så du ser något innan Quarto.

Ja, quarto-installationen verkar stor och krånglig, så vi tar det steg för steg. Hur skall jag tänka kring conda-miljöer?

Tänk två miljöer, inte en soppa.
isescan-revisit (finns redan)

Bara köra ISEScan + Snakemake + dina Python-skript.
Rör den så lite som möjligt. Om den går sönder står analysen stilla.
En andra miljö för rapporten, t.ex. isescan-report

Här får Quarto, R och plotly ligga. Då kan du experimentera utan att knäcka ISEScan.

conda create -n isescan-report -c conda-forge python=3.11 quarto r-base r-plotly r-dt r-readr r-tidyverse
conda activate isescan-report
quarto --version

Byt miljö med flit:

köra ISEScan / build_genome_stats.py  →  isescan-revisit
rendera dashboard                     →  isescan-report

Vad du inte ska göra

Inte conda install quarto inuti isescan-revisit.
Inte blanda apt-R och conda-R i samma huvud. Du har redan r-base via apt; den kan du ignorera när conda-Rapportmiljön finns (which R ska då peka på miniconda).
Om Quarto via conda känns för tungt

Låt isescan-revisit vara orörd och gör första HTML:en med plotly i den miljön. Quarto-miljön kan vänta.

Nästa steg om du väljer två miljöer: skapa isescan-report med kommandot ovan och klistra in om något klagar.

Jag körde conda create -n isescan-report -c conda-forge python=3.11 quarto r-base r-plotly r-dt r-readr r-tidyverse
conda activate isescan-report
quarto --version och allt gick fint. Men detta känns som ett stort steg. Hur skall jag dokumentera detta och tänka kring git och config-filer?

Det är ett stort steg i din miljö, inte i koden. Git ska spegla det lilla som är delbart.
Vad som hör hemma var
Sak	Git?	Varför
env/environment-report.yml	ja	så du kan återskapa isescan-report
reports/*.qmd	ja	själva sidan
reports/*.html	nej (än)	stor, återskapas med quarto render
notes/labbok.md	ja	beslutet
conda-paketen på disken	nej	ligger i ~/miniconda3/envs/

Exportera miljön en gång:

conda activate isescan-report
conda env export --from-history > env/environment-report.yml

--from-history ger de paket du bad om, inte hela trädet.

Lägg i .gitignore:

reports/*.html
reports/.quarto/

Config

Ingen ny paths.yaml. Rapporten läser results/tables/genome_stats.tsv med relativ sökväg från projektroten. Skriv i labboken vilken miljö som renderar.
Labbok

## 2026-08-22 — rapportmiljö
Beslut: två conda-miljöer.
- isescan-revisit = ISEScan + Python-statistik
- isescan-report = Quarto + R (plotly, DT, readr, tidyverse)
Skapad med conda-forge. Export: env/environment-report.yml
Rendera alltid från ~/isescan-revisit med den andra miljön aktiverad.

Git nu

git add env/environment-report.yml .gitignore notes/labbok.md
git commit -m "Separat Quarto/R-miljö för rapporten"
git push

.qmd committar du när första sidan finns.

Tänk: körning är miljö A, visning är miljö B, sanningen är TSV-filerna. Git versionerar recept och text, inte HTML eller conda-cachen.

Vad behöver jag göra nu?

Nästa konkreta sak: första sidan.

    Skapa mappen och filen

conda activate isescan-report
cd ~/isescan-revisit
mkdir -p reports

    Klistra in Quarto-mallen i reports/is_oversikt.qmd (den från förra steget).
    Rendera från projektroten (så sökvägen till results/tables/genome_stats.tsv stämmer):

quarto render reports/is_oversikt.qmd

    Öppna HTML:n i Windows:
    \\wsl$\Ubuntu\home\eris\isescan-revisit\reports\is_oversikt.html
    (exakt namn syns i utskriften).
    En rad i labboken + git add reports/is_oversikt.qmd.

Om quarto render klagar: klistra in hela felet. Om det lyckas: då först pratar vi om mer hover, familjer och fragment.

Kan du skriva ut quarto-mallen igen?

Spara som reports/is_oversikt.qmd.

---
title: "IS-översikt"
format:
  dashboard:
    theme: default
---

```{r}
#| echo: false
library(readr)
library(plotly)
library(DT)

stats <- read_tsv("results/tables/genome_stats.tsv", show_col_types = FALSE)
```

## Rad {height="20%"}

```{r}
#| content: valuebox
#| title: "Genom"
list(value = nrow(stats))
```

```{r}
#| content: valuebox
#| title: "Median % IS"
list(value = round(median(stats$pct_genome_is, na.rm = TRUE), 2))
```

## Rad

```{r}
#| title: "Genomstorlek mot andel IS"
plot_ly(
  stats,
  x = ~genome_bp / 1e6,
  y = ~pct_genome_is,
  color = ~assembly_level,
  text = ~paste(sample, top_family, sep = "<br>"),
  hoverinfo = "text",
  type = "scatter",
  mode = "markers"
) |>
  layout(xaxis = list(title = "Genom (Mbp)"), yaxis = list(title = "% IS"))
```

## Rad

```{r}
#| title: "Klickbar tabell"
datatable(
  stats[, c("sample", "assembly_level", "genome_bp", "n_contigs",
            "n50", "n_is", "n_complete", "n_partial", "pct_genome_is",
            "top_family")],
  options = list(pageLength = 15),
  filter = "top"
)
```

Render från ~/isescan-revisit med isescan-report aktiverad:

quarto render reports/is_oversikt.qmd

fick detta när jag körde kommandot :
1/10
2/10 [unnamed-chunk-1]
Error:
! 'results/tables/genome_stats.tsv' does not exist in current working
  directory: '/home/eris/isescan-revisit/reports'.
Backtrace:
    ▆
 1. ├─readr::read_tsv("results/tables/genome_stats.tsv", show_col_types = FALSE)
 2. │ └─vroom::vroom(...)
 3. │ └─vroom:::vroom_(...)
 4. └─vroom (local) <fn>("results/tables/genome_stats.tsv")
 5. └─vroom:::check_path(path)
 6. └─cli::cli_abort(msg, call = call)
 7. └─rlang::abort(...)
Quitting from is_oversikt.qmd:8-15 [unnamed-chunk-1]
Execution halted

Quarto kör från mappen där .qmd ligger, alltså reports/. Sökvägen måste gå ett steg upp.

Byt raden till:

stats <- read_tsv("../results/tables/genome_stats.tsv", show_col_types = FALSE)

Spara och kör igen från ~/isescan-revisit:

quarto render reports/is_oversikt.qmd

Alternativ (om du vill behålla results/... utan ..): lägg i YAML-huvudet:

execute:
  dir: ..

En av de två räcker. .. är minst.

Hur ser jag resultatet?

Efter en lyckad quarto render ligger sidan här:

~/isescan-revisit/reports/is_oversikt.html

Från Windows-utforskaren klistra in:

\\wsl$\Ubuntu\home\eris\isescan-revisit\reports\is_oversikt.html

Dubbelklicka, eller högerklicka → Öppna med → Chrome.

Från WSL (öppnar Windows-standardwebbläsare):

explorer.exe "$(wslpath -w ~/isescan-revisit/reports/is_oversikt.html)"

Om filen saknas gick inte renderingen klart — kolla att du ser Output created: is_oversikt.html i terminalen.

Strålande resultat, dags för git igen!

Lägg till källan, inte HTML:n (om du gitignorerade den).

cd ~/isescan-revisit
git add reports/is_oversikt.qmd notes/labbok.md env/environment-report.yml .gitignore
git status

HTML och .quarto/ ska inte vara staged.

git commit -m "Första Quarto-dashboarden för genome_stats"
git push

Saknas environment-report.yml eller labboksraden är det okej — committa det som faktiskt ändrats.

Jag vill också ha ett mänskligt läsbart namn för genomen i tabellen som visas. som det är nu står bara koden (GCF eller något). Det vore bra med fylogeni-information, alltså om det är en nostoc eller escherichia vi talar om, finns den infon i filer eller kräver det ett extra steg med ev. web-hämntning?

Artnamnet har du redan, utan nätet.

I config/ncbi_sample.tsv finns organism_name och taxid från NCBI-listan (Escherichia coli, Nostoc sp., …). Det är inget extra API-anrop.

Det som saknas är att det inte följde med till samples.tsv / genome_stats.tsv (eller att dashboarden inte visar kolumnen).
1. Slå ihop namnen (lokalt)

conda activate isescan-revisit
python - <<'PY'
import pandas as pd
stats = pd.read_csv("results/tables/genome_stats.tsv", sep="\t")
ncbi = pd.read_csv("config/ncbi_sample.tsv", sep="\t")
keep = ncbi[["sample", "organism_name", "taxid"]].drop_duplicates("sample")
out = stats.merge(keep, on="sample", how="left")
out.to_csv("results/tables/genome_stats.tsv", sep="\t", index=False)
print(out[["sample", "organism_name"]].head())
PY

Lägg organism_name i DT-tabellen i .qmd (första kolumn efter sample).
2. Fylogeni (stam / klass / släkte)

organism_name är bara det NCBI skrev på assemblyn. Fylum och klass finns inte i FASTA eller ISEScan-TSV.

Då behövs ett extra steg, men inte per-genom-webbsökning:

    taxid har du redan
    ladda ner NCBI:s taxdump en gång och kör t.ex. taxonkit lineage
    eller GTDB om du vill ha modern bakterietaxonomi

Det är en lokal tabell taxid → phylum, class, genus.
Rekommendation nu

Visa organism_name i dashboarden. Släkte får du oftast som första ordet (Escherichia, Nostoc). Vänta med full lineage tills översikten sitter.

Säg till om du vill att build_genome_stats.py alltid slår ihop från ncbi_sample.tsv automatiskt.

Ja, ändra build_genome_stats på det viset. Skriv även en kommentar i py-filen som anger hur olika värden beräknats, så kolumn-huvuden etc blir riktigt begripliga

Ersätt scripts/build_genome_stats.py med filen nedan. Den slår ihop organism_name och taxid från config/ncbi_sample.tsv (samples.tsv vinner om värdet redan finns). Kolumnförklaringen står i docstring högst upp.

Kör om:

conda activate isescan-revisit
python scripts/build_genome_stats.py

I reports/is_oversikt.qmd, lägg in organism_name i tabellen:

datatable(
  stats[, c("sample", "organism_name", "assembly_level", "genome_bp",
            "n_contigs", "n50", "n_is", "n_complete", "n_partial",
            "pct_genome_is", "top_family")],
  options = list(pageLength = 15),
  filter = "top"
)

Rendera med isescan-report efteråt.

#!/usr/bin/env python3
"""Bygg results/tables/genome_stats.tsv från FASTA + ISEScan-TSV.

En rad per genom i config/samples.tsv.

Kolumner (hur de räknas)
-------------------------
sample            Id från samples.tsv (t.ex. GCF_013378015v1).
organism_name     Artnamn från config/ncbi_sample.tsv, matchat på sample.
                  Saknas rad där → tomt (egna MAG/test utan NCBI-rad).
taxid             NCBI taxonomy-id från ncbi_sample.tsv, samma matchning.
assembly_level    Från samples.tsv om kolumnen finns, annars ncbi_sample.tsv.
source            Från samples.tsv om den finns (ncbi / eget / test).
accession         Från samples.tsv eller ncbi_sample.tsv.
fasta             Filnamn i data_raw, inte full sökväg.
genome_bp         Summa av alla contig-längder i FASTA (sekvensrader; rubriker ignoreras).
n_contigs         Antal FASTA-poster (antal '>' ).
n50               Contiglängd där kumulativ summa först når minst halva
                  genome_bp, när contigs sorterats längst först.
longest_contig    Längsta FASTA-posten.
n_is              Antal rader i ISEScan-TSV = predikterade element.
n_complete        Antal rader där type är c (versalokänsligt).
n_partial         Antal rader där type är p.
is_bp             Summa isLen (eller len4is). Saknas den: summa (isEnd-isBegin+1).
                  Överlapp räknas dubbelt — medvetet enkelt mått.
n_families        Unika värden i family.
top_family        Vanligaste family (antal element, inte bp).
pct_genome_is     100 * is_bp / genome_bp. Kan bli >100 vid överlapp.
isescan_tsv       Sökväg till TSV som användes (felsökning).
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
    p.add_argument(
        "--ncbi-sample",
        type=Path,
        default=Path("config/ncbi_sample.tsv"),
        help="Valfri NCBI-katalog med organism_name och taxid",
    )
    p.add_argument("--out", type=Path, default=Path("results/tables/genome_stats.tsv"))
    return p.parse_args()

def load_paths(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)

def load_ncbi_lookup(path: Path) -> pd.DataFrame:
    if not path.is_file():
        return pd.DataFrame(columns=["sample"])
    df = pd.read_csv(path, sep="\t", dtype=str)
    if "sample" not in df.columns:
        return pd.DataFrame(columns=["sample"])
    keep = [c for c in ("sample", "organism_name", "taxid", "accession", "assembly_level") if c in df.columns]
    return df[keep].drop_duplicates(subset=["sample"], keep="first")

def fasta_stats(fasta: Path) -> dict:
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
        return {"genome_bp": 0, "n_contigs": 0, "n50": 0, "longest_contig": 0}

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
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, sep="\t", dtype=str, low_memory=False)

def col(df: pd.DataFrame, *names: str) -> str | None:
    lower = {c.lower(): c for c in df.columns}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    return None

def summarize_hits(hits: pd.DataFrame) -> dict:
    empty = {
        "n_is": 0, "n_complete": 0, "n_partial": 0,
        "is_bp": 0, "n_families": 0, "top_family": "",
    }
    if hits.empty:
        return empty

    type_col = col(hits, "type")
    family_col = col(hits, "family")
    begin_col = col(hits, "isBegin")
    end_col = col(hits, "isEnd")
    len_col = col(hits, "isLen", "len4is")

    n_complete = n_partial = 0
    if type_col:
        types = hits[type_col].str.lower().str.strip()
        n_complete = int((types == "c").sum())
        n_partial = int((types == "p").sum())

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
        "n_is": len(hits),
        "n_complete": n_complete,
        "n_partial": n_partial,
        "is_bp": int(is_bp),
        "n_families": n_families,
        "top_family": top_family,
    }

def summarize_genome(sample, fasta, isescan_tsv, extra=None):
    row = {"sample": sample}
    if extra:
        row.update(extra)
    row.update(fasta_stats(fasta))
    row.update(summarize_hits(read_isescan_tsv(isescan_tsv)))
    genome_bp = row["genome_bp"]
    row["pct_genome_is"] = round(100.0 * row["is_bp"] / genome_bp, 4) if genome_bp else 0.0
    row["isescan_tsv"] = str(isescan_tsv)
    row["fasta"] = fasta.name
    return row

def pick_extra(rec, ncbi_row):
    extra = {}
    for key in ("organism_name", "taxid", "assembly_level", "source", "accession"):
        val = rec.get(key)
        if val is not None and str(val).strip() not in ("", "nan"):
            extra[key] = str(val).strip()
        elif ncbi_row and key in ncbi_row:
            nval = ncbi_row.get(key)
            if nval is not None and str(nval).strip() not in ("", "nan"):
                extra[key] = str(nval).strip()
    return extra

def main() -> None:
    args = parse_args()
    cfg = load_paths(args.paths)
    data_raw = Path(cfg["data_raw"])
    isescan_dir = Path(cfg.get("isescan_outdir", "results/isescan"))

    samples = pd.read_csv(args.samples, sep="\t", dtype=str)
    if "sample" not in samples.columns or "fasta" not in samples.columns:
        raise SystemExit("samples.tsv måste ha kolumnerna sample och fasta")

    ncbi = load_ncbi_lookup(args.ncbi_sample)
    ncbi_map = ncbi.set_index("sample").to_dict(orient="index") if len(ncbi) else {}

    rows = []
    for rec in samples.to_dict(orient="records"):
        sample = rec["sample"].strip()
        fasta = data_raw / rec["fasta"].strip()
        tsv = isescan_dir / sample / f"{sample}.tsv"
        extra = pick_extra(rec, ncbi_map.get(sample))
        if not fasta.is_file():
            print(f"SAKNAR FASTA: {sample} -> {fasta}")
            continue
        if not tsv.is_file():
            print(f"SAKNAR ISEScan-TSV: {sample} -> {tsv}")
            continue
        rows.append(summarize_genome(sample, fasta, tsv, extra))
        print(f"OK  {sample}")

    out = pd.DataFrame(rows)
    preferred = [
        "sample", "organism_name", "taxid", "assembly_level", "source",
        "accession", "fasta", "genome_bp", "n_contigs", "n50",
        "longest_contig", "n_is", "n_complete", "n_partial", "is_bp",
        "pct_genome_is", "n_families", "top_family", "isescan_tsv",
    ]
    cols = [c for c in preferred if c in out.columns] + [c for c in out.columns if c not in preferred]
    out = out[cols]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, sep="\t", index=False)
    print(f"Skrev {len(out)} rader till {args.out}")

if __name__ == "__main__":
    main()

vilken miljö skall jag använda när jag kör detta?

isescan-revisit.

Det är Python + pandas + pyyaml, samma som build_genome_stats hör till.

conda activate isescan-revisit
cd ~/isescan-revisit
python scripts/build_genome_stats.py

isescan-report är bara när du kör quarto render.

## Här är min nuvarande is_oversikt.qmd.:

## title: "IS-översikt" format:   dashboard:     theme: default

#| echo: false
library(readr)
library(plotly)
library(DT)
stats <- read_tsv("../results/tables/genome_stats.tsv", show_col_types = FALSE)

## Rad {height="20%"}

#| content: valuebox
#| title: "Genom"
list(value = nrow(stats))

#| content: valuebox
#| title: "Median % IS"
list(value = round(median(stats$pct_genome_is, na.rm = TRUE), 2))

## Rad

#| title: "Genomstorlek mot andel IS"
plot_ly(
  stats,
  x = ~genome_bp / 1e6,
  y = ~pct_genome_is,
  color = ~assembly_level,
  text = ~paste(sample, top_family, sep = "<br>"),
  hoverinfo = "text",
  type = "scatter",
  mode = "markers"
) |>
  layout(xaxis = list(title = "Genom (Mbp)"), yaxis = list(title = "% IS"))

## Rad

#| title: "Klickbar tabell"
datatable(
  stats[, c("sample", "assembly_level", "genome_bp", "n_contigs",
            "n50", "n_is", "n_complete", "n_partial", "pct_genome_is",
            "top_family")],
  options = list(pageLength = 15),
  filter = "top"
)
kan du lägga till raden med namn?

Byt ut hela reports/is_oversikt.qmd mot detta (organism_name i hover och i tabellen):

---
title: "IS-översikt"
format:
  dashboard:
    theme: default
---

```{r}
#| echo: false
library(readr)
library(plotly)
library(DT)

stats <- read_tsv("../results/tables/genome_stats.tsv", show_col_types = FALSE)
```

## Rad {height="20%"}

```{r}
#| content: valuebox
#| title: "Genom"
list(value = nrow(stats))
```

```{r}
#| content: valuebox
#| title: "Median % IS"
list(value = round(median(stats$pct_genome_is, na.rm = TRUE), 2))
```

## Rad

```{r}
#| title: "Genomstorlek mot andel IS"
plot_ly(
  stats,
  x = ~genome_bp / 1e6,
  y = ~pct_genome_is,
  color = ~assembly_level,
  text = ~paste(sample, organism_name, top_family, sep = "<br>"),
  hoverinfo = "text",
  type = "scatter",
  mode = "markers"
) |>
  layout(xaxis = list(title = "Genom (Mbp)"), yaxis = list(title = "% IS"))
```

## Rad

```{r}
#| title: "Klickbar tabell"
datatable(
  stats[, c("sample", "organism_name", "assembly_level", "genome_bp",
            "n_contigs", "n50", "n_is", "n_complete", "n_partial",
            "pct_genome_is", "top_family")],
  options = list(pageLength = 15),
  filter = "top"
)
```

Kör build_genome_stats.py först så kolumnen finns, sen:

conda activate isescan-report
cd ~/isescan-revisit
quarto render reports/is_oversikt.qmd

(isescan-report) eris@DESKTOP-17ENJH0:~/isescan-revisit$ git status
On branch main
Your branch is up to date with 'origin/main'.
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified: notes/labbok.md
        modified: reports/is_oversikt.qmd
        modified: results/tables/genome_stats.tsv
        modified: scripts/build_genome_stats.py
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        reports/is_oversikt_files/
        results/tables/.gitkeep
no changes added to commit (use "git add" and/or "git commit -a")
 
hur addar/kommitar/pushar jag nu?

Lägg till källan och tabellen. Hoppa över Quarto-hjälpfilerna och .gitkeep.

git add notes/labbok.md reports/is_oversikt.qmd
git add results/tables/genome_stats.tsv scripts/build_genome_stats.py

Lägg i .gitignore om det inte redan står:

reports/*_files/
reports/*.html
results/tables/.gitkeep

git add .gitignore
git status

Du ska inte se reports/is_oversikt_files/ som staged.

git commit -m "organism_name i genome_stats och dashboard"
git push

Om jag vill ladda ner och analysera fler genom, är det då select_ncbi_sample.py jag skall köra först?

Ja, om de ska slumpas från NCBI-listan. Kedjan är densamma, bara fler rader.

    select_ncbi_sample.py — höj t.ex. --n-complete och --n-contig (samma --summary och --seed ger samma 40 plus nya om du ökar n; samma seed + samma n ger samma 40). Vill du behålla de 40 och lägga till fler: antingen ett nytt seed och slå ihop TSV:erna, eller öka n och acceptera att urvalet räknas om.
    download_ncbi_sample.py — hoppar över det som redan finns.
    Uppdatera samples.tsv (de nya sample + fasta).
    snakemake -s workflow/Snakefile -c 2 — kör bara saknade.
    build_genome_stats.py och quarto render.

Egna MAG eller extra genom du redan har: inte select-skriptet. Lägg FASTA i data/raw och en rad i samples.tsv.

Lista och seed lämnar du orörda så länge du vill kunna förklara vilka 40 som var först.

Jag vill inte slå ihop tsv:erna manuellt. Om gör n=80 tar den väl ut de gamla 40 och sedan 40 till?

Nej, lita inte på det.

sample(n=80, random_state=42) är ett nytt stickprov av storlek 80, inte “de gamla 40 plus 40 till”. Samma seed betyder bara att just n=80 blir densamma nästa gång du ber om 80 — inte att den innehåller n=40-körningen.

Gör så här i stället: slumpa fler bland dem som inte redan ligger i ncbi_sample.tsv, och lägg till raderna.

Kör (samma miljö isescan-revisit):

python - <<'PY'
import pandas as pd
from pathlib import Path
from scripts.select_ncbi_sample import (
    read_assembly_summary,
    filter_candidates,
    sample_group,
    to_sample_table,
)

summary = read_assembly_summary(
    Path("data/meta/assembly_summary_refseq_bacteria_2026-08-21.txt")
)
old = pd.read_csv("config/ncbi_sample.tsv", sep="\t")
used = set(old["accession"])

n_new_c = n_new_d = 20
seed = 43  # annat seed än 42, dokumentera i labboken

complete = filter_candidates(summary, "Complete Genome")
contig = filter_candidates(summary, "Contig")
complete = complete[~complete["assembly_accession"].isin(used)]
contig = contig[~contig["assembly_accession"].isin(used)]

extra = pd.concat(
    [
        to_sample_table(sample_group(complete, n_new_c, seed, "complete"), "complete"),
        to_sample_table(sample_group(contig, n_new_d, seed, "contig"), "contig"),
    ],
    ignore_index=True,
)
out = pd.concat([old, extra], ignore_index=True)
out.to_csv("config/ncbi_sample.tsv", sep="\t", index=False)
print(f"Var {len(old)}, blev {len(out)}")
PY

Sedan: download_ncbi_sample.py → uppdatera samples.tsv → Snakemake → build_genome_stats.py.

Skriv i labboken: första 40 seed 42, tillägg seed 43, 20+20 extra. Då är urvalet fortfarande förklarbart.

Osmidigt. Kan du skriva ett nytt program, increase_select_ncbi... som slumpar fram ett antal genom att undersöka, men kontrollerar om genomet redan finns i listan av tidigare nedladdade genom?

Spara som scripts/increase_select_ncbi.py. Det återanvänder filtren från select_ncbi_sample.py, hoppar över accession i ncbi_sample.tsv och filer i data_raw, och lägger till rader sist.

#!/usr/bin/env python3
"""Lägg till fler slumpade NCBI-genom utan att röra de som redan valts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from select_ncbi_sample import (
    filter_candidates,
    read_assembly_summary,
    sample_group,
    to_sample_table,
)

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Slumpa fler genom och lägg till i ncbi_sample.tsv"
    )
    p.add_argument(
        "--summary",
        type=Path,
        default=Path("data/meta/assembly_summary_refseq_bacteria_2026-08-21.txt"),
    )
    p.add_argument(
        "--existing",
        type=Path,
        default=Path("config/ncbi_sample.tsv"),
    )
    p.add_argument("--paths", type=Path, default=Path("config/paths.yaml"))
    p.add_argument("--n-complete", type=int, default=20)
    p.add_argument("--n-contig", type=int, default=20)
    p.add_argument("--seed", type=int, default=43)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()

def used_accessions(existing: pd.DataFrame) -> set[str]:
    acc: set[str] = set()
    if "accession" in existing.columns:
        acc |= set(existing["accession"].dropna().str.strip())
    if "sample" in existing.columns:
        acc |= set(existing["sample"].dropna().str.replace("v", ".", regex=False))
    return {a for a in acc if a}

def used_from_raw(data_raw: Path) -> set[str]:
    found: set[str] = set()
    if not data_raw.is_dir():
        return found
    for path in data_raw.iterdir():
        name = path.name
        if "_genomic.fna" in name:
            found.add(name.replace("_genomic.fna", "").replace(".gz", ""))
    return found

def main() -> None:
    args = parse_args()
    if not args.summary.is_file():
        raise SystemExit(f"Hittar inte summary: {args.summary}")
    if not args.existing.is_file():
        raise SystemExit(f"Hittar inte {args.existing} — kör select_ncbi_sample.py först")

    old = pd.read_csv(args.existing, sep="\t", dtype=str)
    used = used_accessions(old)

    if args.paths.is_file():
        cfg = yaml.safe_load(args.paths.read_text(encoding="utf-8"))
        used |= used_from_raw(Path(cfg.get("data_raw", "data/raw")))

    summary = read_assembly_summary(args.summary)
    complete = filter_candidates(summary, "Complete Genome")
    contig = filter_candidates(summary, "Contig")
    complete = complete[~complete["assembly_accession"].isin(used)]
    contig = contig[~contig["assembly_accession"].isin(used)]

    print(f"Redan använda accession: {len(used)}")
    print(f"Kvar complete: {len(complete)}")
    print(f"Kvar contig:   {len(contig)}")
    print(f"Seed: {args.seed}")

    extra_parts = []
    if args.n_complete > 0:
        extra_parts.append(
            to_sample_table(
                sample_group(complete, args.n_complete, args.seed, "complete"),
                "complete",
            )
        )
    if args.n_contig > 0:
        extra_parts.append(
            to_sample_table(
                sample_group(contig, args.n_contig, args.seed, "contig"),
                "contig",
            )
        )
    extra = pd.concat(extra_parts, ignore_index=True) if extra_parts else pd.DataFrame()
    out = pd.concat([old, extra], ignore_index=True)

    print(f"Lägger till {len(extra)} rader (totalt {len(out)})")
    if args.dry_run:
        print(extra.to_string(index=False))
        print("Dry-run: ingen fil skriven")
        return

    out.to_csv(args.existing, sep="\t", index=False)
    print(f"Skrev {args.existing}")

if __name__ == "__main__":
    main()

conda activate isescan-revisit
cd ~/isescan-revisit

python scripts/increase_select_ncbi.py --n-complete 20 --n-contig 20 --seed 43 --dry-run
python scripts/increase_select_ncbi.py --n-complete 20 --n-contig 20 --seed 43

Därefter samma kedja: download_ncbi_sample.py → nya rader i samples.tsv → Snakemake → build_genome_stats.py.

Skriv seed 43 (och nästa gång 44) i labboken. Originalurvalet med seed 42 lämnas orört.

Är dessa rader korrekta för nästa del:
conda activate isescan-revisit
python scripts/download_ncbi_sample.py 
  --samples config/ncbi_sample.tsv 
  --outdir data/raw 
  --log results/logs/download_failures.log

Ja. Kör dem från ~/isescan-revisit. Skriptet hoppar över FASTA som redan finns.

Efter nedladdningen måste nya rader in i config/samples.tsv (Snakemake läser den, inte ncbi_sample.tsv). Sedan:

snakemake -s workflow/Snakefile -n
snakemake -s workflow/Snakefile -c 2
python scripts/build_genome_stats.py

Vad gör jag nu?
2 / 2

Kolla var du står, sen nästa sak i kedjan.

cd ~/isescan-revisit
conda activate isescan-revisit
wc -l config/ncbi_sample.tsv config/samples.tsv
ls data/raw/*_genomic.fna | wc -l

    Fler rader i ncbi_sample.tsv än i samples.tsv: kopiera de nya sample + fasta till samples.tsv (samma kolumner som förut).
    FASTA saknas: kör download_ncbi_sample.py igen (hoppar över färdiga).
    samples.tsv är ikapp men ISEScan saknas:

snakemake -s workflow/Snakefile -n
snakemake -s workflow/Snakefile -c 2

När Snakemake är klar:

python scripts/build_genome_stats.py
conda activate isescan-report
quarto render reports/is_oversikt.qmd

Skriv seed 43 och hur många extra genom i labboken, sen git.

Klistra in wc/ls-siffrorna om du är osäker på vilket steg du är på.

Allt gick bra! Om jag vill ladda ner 20 genom till, skall jag då köra python scripts/increase_select_ncbi.py --n-complete 20 --n-contig 20 --seed 43 igen, eller ändra seed?

Byt seed. Kör inte 43 igen som om det vore samma kommando.

Seed 43 är redan “första påbyggnaden”. Nästa blir 44, sedan 45. Samma seed på en annan kvarvarande lista ger nya genom, men labboken blir svårläst.

python scripts/increase_select_ncbi.py --n-complete 10 --n-contig 10 --seed 44

--n-complete 20 --n-contig 20 är 40 genom. Vill du bara 20 totalt: 10+10, eller 20+0 om bara complete.

Sen samma kedja: download → samples.tsv → Snakemake → build_genome_stats.py. Anteckna “påbyggnad 2, seed 44, 10+10”.

Här är min nuvarande readme.md

# ISEScan revisit

Modern omtagning av homology-baserad IS-detektion.

## Data

Rå FASTA ligger i sökvägen som anges i config/paths.yaml (data_raw).
Lägg till prover i config/samples.tsv.

## Kör

    conda env create -f env/environment.yml
    conda activate isescan-revisit
    snakemake -s workflow/Snakefile -c 2

## Anteckningar

Skriv beslut och resultatvägar i notes/labbok.md.
Spara inte misslyckade tester där.
 
 
Kan du skriva en ny, avsedd för vetenskapligt belästa lekmän? Det skall kortfattat förklara transposasers roll i bakterier och säga att det här projektet är en "pipeline" under utveckling för att indentifiera transposaser i bakterier-genom. Skriv en föreslagen arbetsväg för att använda projektet (kommandon att köra -> resultat i lekmannaspråk av kommandot). Poängtera att detta är ett pågående arbete, långt ifrån färdigt för allmänt användande.

Här är en ny README.md du kan klistra in.

# ISEScan revisit

Ett pågående arbete för att hitta **insertionssekvenser (IS-element)** i bakteriegenom.

Det här är **inte** ett färdigt verktyg för allmän användning. Det är en personlig, dokumenterad pipeline under utveckling: kod, urval och resultat ändras fortfarande.

## Varför IS-element?

Bakterier bär ofta korta, flyttbara DNA-bitar som kallas insertionssekvenser. De kodar oftast en **transposas** — ett enzym som kan klippa ut elementet och sätta in det någon annanstans i genomet.

När det händer kan gener slås av, slås på eller flyttas mellan stammar. IS-element förklarar därför en del av hur bakterier snabbt ändrar sig, och de gör samtidigt genom svåra att sätta ihop: samma sekvens finns på många ställen.

Det här projektet räknar var sådana element sitter, om de ser kompletta eller avbrutna ut, och hur stor del av genomet de tar.

## Vad pipelinen gör just nu

1. Väljer slumpade bakteriegenom från NCBI (kompletta och contig-nivå).
2. Laddar ner FASTA-filerna.
3. Kör [ISEScan](https://github.com/xiezhq/ISEScan) via Snakemake.
4. Sammanfattar varje genom i en tabell och en enkel HTML-översikt.

Egna metagenom-assemblies (MAG) kan läggas till för hand. Storskalig slutsatsdragning och färdig “app” finns inte ännu.

## Två arbetsmiljöer

| Miljö | Användning |
|---|---|
| `isescan-revisit` | Ladda ner genom, köra ISEScan, räkna statistik |
| `isescan-report` | Bygga HTML-översikten med Quarto |

Skapa kör-miljön en gång:

```bash
conda env create -f env/environment.yml
```

Rapportmiljön: se `env/environment-report.yml` och `notes/labbok.md`.

## Föreslagen arbetsväg

Arbeta i Linux (t.ex. WSL) från projektmappen. Rå FASTA pekas ut i `config/paths.yaml`.

**Välj genom (första gången)**  
`python scripts/select_ncbi_sample.py`  
→ en lista i `config/ncbi_sample.tsv` (accessions, artnamn, nedladdningslänkar). Inga sekvenser än.

**Lägg till fler senare**  
`python scripts/increase_select_ncbi.py --n-complete 10 --n-contig 10 --seed 44`  
→ nya rader *efter* de gamla. Redan valda genom slumpas inte om. Byt seed varje gång och skriv det i labboken.

**Ladda ner sekvenserna**  
`python scripts/download_ncbi_sample.py --samples config/ncbi_sample.tsv --outdir data/raw`  
→ FASTA-filer på disk. Avbrutna hämtningar kan köras om; färdiga filer hoppas över. Fel loggas i `results/logs/download_failures.log`.

**Körlista för analysen**  
Kopiera `sample` och `fasta` från `ncbi_sample.tsv` till `config/samples.tsv`.  
`ncbi_sample.tsv` = vad som valts hos NCBI.  
`samples.tsv` = vad ISEScan faktiskt ska köra (NCBI + ev. egna filer).

**Hitta IS-element**  
```bash
conda activate isescan-revisit
snakemake -s workflow/Snakefile -n    # torrkörning: visar vad som skulle göras
snakemake -s workflow/Snakefile -c 2  # riktig körning, två processorkärnor
```  
→ per genom: tabell, GFF och sammanfattning under `results/isescan/`.  
Snakemake hoppar över genom som redan är klara.

**Räkna översiktsmått**  
`python scripts/build_genome_stats.py`  
→ `results/tables/genome_stats.tsv`: genomstorlek, andel DNA som predikteras som IS, complete/partial, vanligaste IS-familj, artnamn.

**Titta på resultatet**  
```bash
conda activate isescan-report
quarto render reports/is_oversikt.qmd
```  
→ `reports/is_oversikt.html` med plot och klickbar tabell.

**Anteckna**  
Beslut och seed hör hemma i `notes/labbok.md`, inte varje misslyckat testkommando.

## Status

Fungerar som laborativ kedja på en arbetsstation. Saknas bland annat: MAG-urval från NCBI, fragmentlängd mot förväntad transposas, systematiskt test av contig-ändar, och en stabil publikation av sidan. Använd resultaten som utforskning, inte som facit.

## Bakgrund

Omtagning av en äldre homology-baserad IS-analys (BLASTX + Biopython). Detektorn nu är ISEScan (Xie & Tang, 2017).


PhD Bioinformatician to STEM Instructor Roles - Grok
