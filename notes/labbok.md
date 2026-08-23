# Labbok — ISEScan revisit

## 2026-08-20
Skapade projektstruktur.
Körde script/scripts/Program_to_make_file_structure.py som skapar folderstrukturen
Beslut: sökvägar bara i `config/paths.yaml`.
Beslut: behåll partial IS (`remove_short_is: false`).

## 2026-08-20
Anteckning: Ändrade i /README.md från
snakemake -s workflow/Snakefile -c 4 
till 
c-2 
så jag kan köra andra processer. Har fortfarande inte kört eller undersökt snakemake-kommandot.

Ändrade även i paths.yaml så att det står:

# ISEScan-inställningar
nthread: 2
remove_short_is: false

Anteckning: Länk till isescan:https://github.com/xiezhq/ISEScan

## 2026-08-20
Anteckning:Körde conda-kommando för att skapa miljö (och ladda ner saker)
Instruktioner för konta finns i /notes/Hur_använda_conda.md
Kommando: conda env create -f env/environment.yml
Resultat: Misslyckat eftersom ISEscan måste köras på linux





## 2026-08-20
Anteckning: Måste installera linux för att köra ISEScan
Anteckning: För att gå ur och komma tillbaks till ubuntu i powershell:
exit tar dig tillbaka till PowerShell.
Vill du ha Ubuntu igen: skriv wsl eller ubuntu i PowerShell.
Kommando: wsl --install från windows powershell som administratör

output i rutan: Create a default Unix user account: eris (jag valde eris och tryckte return)


Resultat: installation lyckades, linux ligger i (\\wsl$\Ubuntu\home\eris - skriv detta som adress i utforskaren).
conda --version misslyckades.


## 2026-08-20
Anteckning: Körde detta för att installera conda:
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

accepterade default sökväg /home/eris/miniconda3
Resultat: conda --version visar nu conda 26.5.3

## 2026-08-20
cd till rätt folder:
Resultat: ubuntu är nu i windows-foldern isescan-revisit
Kommando: cd /mnt/c/Users/Eris/Documents/AAA_IsprojectAug2026/isescan-revisit

## 2026-08-20
Efter att ha installerat ubuntu och conda är jag nu i ubuntu och kan köra kommandot 
Kommando: conda env create -f env/environment.yml
Kommando_from: /mnt/c/Users/Eris/Documents/AAA_IsprojectAug2026/isescan-revisit
Resultat: Lyckades.
# To activate this environment, use
#
#     $ conda activate isescan-revisit
#
# To deactivate an active environment, use
#
#     $ conda deactivate


## 2026-08-20
Startade isescan-revisit miljön för första gången
Kommando: conda activate isescan-revisit
Kommando_from: /mnt/c/Users/Eris/Documents/AAA_IsprojectAug2026/isescan-revisit
Resultat: lyckades

## 2026-08-20
Testade conda-miljön
Kommando: snakemake --version
Resultat:9.24.0
Kommando: isescan.py --help
Resultat: hjälpfil printas

## 2026-08-20
Körde dryrun för snake-filen.
För att göra detta tog jag ett slumpmässigt genom, CP031221_1, från 
D:\g\transposeek2\static\results\CP031221_1
och lade i /mnt/c/Users/Eris/data/isescan-revisit/raw/

Jag ändrade också i filen /config/samples.tsv, i textform ser den ut så här.
sample	fasta
Test_CO031221	CP031221_1_conc.fa

Detta ledde till att ett fel hittades i /config/paths.yaml.
data_raw: /mnt/c/Users/Eris/data/isescan-revisit/raw
skall det stå för att nå raw-foldern från innuti ubuntu.

Kommando: snakemake -s workflow/Snakefile -n
Resultat: misslyckades, se ovan.

## 2026-08-20
Körde dryrun för snake-filen med ändrad filväg

Kommando: snakemake -s workflow/Snakefile -n
Resultat: lyckades

## 2026-08-20
Körde riktigt test på CP031221_1

Kommando: snakemake -s workflow/Snakefile -c 3
Resultat: misslyckades


## 2026-08-20
Problem med skrivrättigheter gjorde att filerna flyttades till linux-foldern:

cp -a /mnt/c/Users/Eris/Documents/AAA_IsprojectAug2026/isescan-revisit ~/isescan-revisit
cd ~/isescan-revisit
conda activate isescan-revisit
rm -rf .snakemake
snakemake -s workflow/Snakefile -c 3

PÅMINNELSE om att jobba i rätt folder
arbeta i ~/isescan-revisit, inte under /mnt/c/...
## 2026-08-20 — första lyckade körningen
Katalog: ~/isescan-revisit
Kommando: snakemake -s workflow/Snakefile -c 2
Input: /mnt/c/Users/Eris/data/isescan-revisit/raw/CP031221_1_conc.fa
Output:
- results/isescan/Test_CO031221/Test_CO031221.tsv
- results/tables/isescan_summary.tsv
Utfall (urval): IS3 49c+23p, IS481 59c+17p, IS982 38c+49p.
Beslut: arbeta alltid i ~/isescan-revisit, inte /mnt/c/...


## 2026-08-20
Github
användarnamn Omnistudent
mail theostenman@yahoo.com
Kommando:git config --global user.name "Omnistudent"
Kommando:git config --global user.email "theostenman@yahoo.com"

## 2026-08-20 — Git och GitHub
Katalog: ~/isescan-revisit
Första gången: git config --global user.name och user.email.
Sedan: git init; git add README.md INSTRUKTIONER.md config env workflow notes scripts .gitignore
(lägg bara till text/kod, inte FASTA, results/isescan eller .snakemake).
git commit -m "Första fungerande ISEScan-pipeline för Test_CO031221"
På GitHub: New repository, private, utan README.
git remote add origin https://github.com/DITTANVANDARNAMN/isescan-revisit.git
git branch -M main
git push -u origin main
Inloggning mot GitHub med token eller gh auth login, inte vanligt lösenord.

## 2026-08-21 — Nedladdning av lista av prokaryot-genom
Skapade filen meta för listan med genom
Kommando:cd ~/isescan-revisit
Kommando:mkdir -p data/meta


## 2026-08-21 — Nedladdning av lista av prokaryot-genom
Laddade ner listan med bakteriegenom från NCBI
Kommando:curl -L -o data/meta/assembly_summary_refseq_bacteria_2026-08-21.txt \
  https://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/assembly_summary.txt

## 2026-08-21
Tillagt i .gitignore:
data/meta/assembly_summary_refseq_bacteria_2026-08-21.txt

## 2026-08-21
Skapade program för att välja genom slumpmässigt.
/scripts/~/isescan-revisit/scripts/select_ncbi_sample.py

Skriptet läser summary-filen, tar bara latest + full + inte exkluderade från RefSeq, slumpar 20 complete och 20 contig med seed 42, och skriver config/ncbi_sample.tsv med accession, organism, ftp_path och tänkt FASTA-namn. Ingen nedladdning.
Kör från ~/isescan-revisit:
Bashconda activate isescan-revisit
python scripts/select_ncbi_sample.py \
  --summary data/meta/assembly_summary_refseq_bacteria_2026-08-21.txt \
  --out config/ncbi_sample.tsv \
  --n-complete 20 \
  --n-contig 20 \
  --seed 42
Byt datum i --summary om din fil heter något annat.

## 2026-08-21
Skapade (med Grok) programmet scripts/download_ncbi_sample.py
Det laddar ner filerna i config/ncbi_sample.tsv till .fna-filer, med kommandot
Kommando: conda activate isescan-revisit
python scripts/download_ncbi_sample.py \
  --samples config/ncbi_sample.tsv \
  --outdir data/raw \
  --log results/logs/download_failures.log

## 2026-08-21
Filerna ncbi_sample.tsv och config/samples.tsv är olika, samples.tsv innehåller de filer som skall köras.
Följande script kopierar från ncbi_sample till samples.tsv
python - <<'PY'
import pandas as pd
ncbi = pd.read_csv("config/ncbi_sample.tsv", sep="\t")
out = ncbi[["sample", "fasta"]].copy()
out["source"] = "ncbi"
out["assembly_level"] = ncbi["assembly_level"]
out.to_csv("config/samples.tsv", sep="\t", index=False)
PY

Kopieringen gick bra

## 2026-08-21
Ändrade i config.yaml, eftersom filerna laddades ner till linux-foldrarna
data_raw: /home/eris/isescan-revisit/data/raw

## 2026-08-21
Körde först dry run
snakemake -s workflow/Snakefile -n
och sedan på riktigt
snakemake -s workflow/Snakefile -c 2

## 2026-08-22
Körningav icescan på 40 genom gick bra.

## 2026-08-22
Installerar quarto och R
med sudo apt install r-base

R --version ger:
R version 4.5.2 (2025-10-31)

## 2026-08-22 — analyslager
Beslut: Quarto + R i WSL, inte Windows.
Installerat: r-base via apt.
Nästa: genome_stats.tsv från ISEScan-TSV + FASTA.
Rör inte workflow/Snakefile för det här steget.

## 2026-08-22 — script som sammanfattar resultat
Byggde scripts/build_genome_stats.py med grok.

Körde conda activate isescan-revisit
python scripts/build_genome_stats.py
head results/tables/genome_stats.tsv

Allt fungerade.

## 2026-08-22 - Ny conda-miljö för statistik
conda create -n isescan-report -c conda-forge python=3.11 quarto r-base r-plotly r-dt r-readr r-tidyverse
conda activate isescan-report
quarto --version
1.9.38

## 2026-08-22
Körde 
conda env export --from-history > env/environment-report.yml

## 2026-08-22 — rapportmiljö
Beslut: två conda-miljöer.
- isescan-revisit = ISEScan + Python-statistik
- isescan-report = Quarto + R (plotly, DT, readr, tidyverse)
Skapad med conda-forge. Export: env/environment-report.yml
Rendera alltid från ~/isescan-revisit med den andra miljön aktiverad.

## 2026-08-22 — första quarto-körningen
quarto render reports/is_oversikt.qmd
lyckades


## 2026-08-22 - körde igen med nytt skript som lägger till organismnamn
conda activate isescan-revisit
cd ~/isescan-revisit
python scripts/build_genome_stats.py

## 2026-08-22 - ai-skrev programmet scripts/increase_select_ncbi.py
Det fungerade och skrev 40 nya rader i ncbi_sample.tsv

conda activate isescan-revisit
cd ~/isescan-revisit

python scripts/increase_select_ncbi.py --n-complete 20 --n-contig 20 --seed 43 --dry-run
python scripts/increase_select_ncbi.py --n-complete 20 --n-contig 20 --seed 43

Körde sedan 
python scripts/download_ncbi_sample.py

## 2026-08-22 Skrev med ai programmet sync_samples_from_ncbi.py
Detta program för över rader från config/ncbi_sample.tsv till samples.tsv
Därefter
python scripts/sync_samples_from_ncbi.py (körde programmet)
snakemake -s workflow/Snakefile -c 2
python scripts/build_genome_stats.py
conda activate isescan-report
quarto render reports/is_oversikt.qmd

allt gick bra, nu 80 genom

## 2026-08-23
Körde
conda activate isescan-revisit
python scripts/increase_select_ncbi.py --n-complete 30 --n-contig 30 --seed 44
download_ncbi_sample.py
python scripts/sync_samples_from_ncbi.py

## 2026-08-23
Ändrade /README.md till något mer läsarvänligt.

## 2026-08-23 - Påminner om vilka genom som analyserades i vår artikel.
Artikeln är Grujcic, Mehrshad, Vigil-Stenman, Lundin & Foster, Current Biology 2025: Stepwise genome evolution … diatom–Richelia.


Kortnamn i artikeln	Vad det är				En accession en läsare hittar
ReuHH01			R. euintracellularis, endobiont		slå i Table S1
ReuHM01			R. euintracellularis, endobiont		Table S1Rint
RC01			R. intracellularis RC01, periplasmisk	GCA_000613065.1
RrhiSC01		R. rhizosoleniae SC01, epibiont		Table S1

eMAG
Texten nämner tio eMAG. Namnen som skrivs ut:

TARA_PON — Candidatus Richelia exalis (Tara Oceans)
DT104 — periplasmisk (98 % ANI mot RintRC01)
MO_192.B10
MO_167.B12
MO_167.B42 — jämförs med RintRC01 / RrhiSC01

plus fem eMAG i samma klad som ReuHH01/ReuHM01 (endobionter); de döps efter GTDB i figur 1, accession bara i Table S1

De tre MO-genomen behandlas som fritt levande släktingar, inte som säkra epibionter.

## 2026-08-23 - Lade till tags till genom.

Ny fil, config/genome_tags.tsv som har följande format:

GCF_013378015v1	test,test2
GCF_006547005v1	test,test3
GCF_000834255v1	tes

Tabellen är tab-separerad.
scripts/build_genome_stats.py inkorporerar nu informationen i genome_tags, och quarto ser till att en kolumn med tags visas i "genom-sektionen"

## 2026-08-23
Den tidigare versionen av workflow/snakefile krashade pga noll IS. Detta är nu korrigerat för i snakefile.

## 2026-08-23
Ändrade is_oversikt.qmd så att den nu genererar klickbara länkar till individuella sidor för varje genom.