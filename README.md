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
Standardskannern är [rust-ise](https://github.com/necoli1822/rust-ise) (MMseqs2 + nyare IS-DB). ISEScan finns kvar som baslinje.

```bash
# en gång: rust-ise-binär + IS-profil-DB
bash scripts/setup_rustise.sh

conda activate isescan-revisit
snakemake -s workflow/Snakefile -n              # torrkörning
snakemake -s workflow/Snakefile -c 16           # rust-ise, många genom parallellt
snakemake -s workflow/Snakefile -c 16 --config scanner=isescan
snakemake -s workflow/Snakefile -c 16 --config scanner=both
```

Korta contigar (< 500 bp, `min_contig_bp` i `config/paths.yaml`) filtreras bort före skanning.  
`nthread: 1` per ISEScan-genom; skala med `-c` i stället. rust-ise använder `rustise_threads`.

→ per genom: tabell, GFF och sammanfattning under `results/rust-ise/` eller `results/isescan/`.  
Vid `scanner=both` skrivs `results/tables/scanner_compare.tsv`.  
Snakemake hoppar över genom som redan är klara.

Litet jämförelseset (fyra små genom):

```bash
python scripts/download_ncbi_sample.py --samples config/ncbi_sample_benchmark.tsv --outdir data/raw
snakemake -s workflow/Snakefile -c 16 --config samples_tsv=config/samples_benchmark.tsv scanner=both
```

**Räkna översiktsmått**  
`python scripts/build_genome_stats.py`  
→ `results/tables/genome_stats.tsv`: genomstorlek, andel DNA som predikteras som IS, complete/partial, vanligaste IS-familj, artnamn.

**Titta på resultatet**  
```bash
conda activate isescan-report
quarto render reports/is_oversikt.qmd
```  
→ `reports/is_oversikt.html` med plot och klickbar tabell.


## Status

Fungerar som laborativ kedja på en arbetsstation. Saknas bland annat: MAG-urval från NCBI, fragmentlängd mot förväntad transposas, systematiskt test av contig-ändar, och en stabil publikation av sidan. Använd resultaten som utforskning, inte som facit.

## Bakgrund

Omtagning av en äldre homology-baserad IS-analys (BLASTX + Biopython). Detektorn nu är ISEScan (Xie & Tang, 2017).