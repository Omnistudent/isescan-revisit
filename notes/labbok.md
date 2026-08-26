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

2026-08-24 — Test av Tims pull request (rust-ise + ML)
Bakgrund
Tim hade öppnat pull request #1: snabbare IS-skanner rust-ise (Rust + MMseqs2 + IS-databas) som alternativ/komplement till ISEScan, plus ett experimentellt andra steg med en DNA-CNN (maskininlärning). Målet var att testa lokalt utan att ändra GitHub main, sedan eventuellt merge:a.
Lokal checkout av PR
Hämtade PR-grenen till en lokal gren (t.ex. pr-1-rust-ise) med git fetch origin pull/1/head:... och checkout. Inget merge till main under dagen — bara lokal test.
Installation av rust-ise

rust-ise kräver Rust/cargo (inte i conda). Först problem med curl | sh (syntax error); installerade Rust via apt och/eller rustup så att cargo fanns.
bash scripts/setup_rustise.sh installerade rust-ise under ~/.cargo/bin (måste finnas i PATH: export PATH="$HOME/.cargo/bin:$PATH").
MMseqs2 i conda-miljön isescan-revisit (conda install -c bioconda mmseqs2 vid behov).

IS-databas (ISOSDB m.m.)
rust-ise söker mot en unionsdatabas (ISOSDB ∪ ISfinder) under resources/rust-ise-db (mmdb_union/profileDb*, manifest_union.tsv).

ISOSDB = Insertion Sequence Open-Source Database (öppen IS-referens från många genom/MAG, bl.a. Kirsch et al. i Cell Host & Microbe 2024).
Under felsökning försvann ibland profilfiler under mmdb_union (kvar bara header-filer) → då klagade MMseqs på att databasen inte fanns. Lösning: bygga om med rust-ise build-db --fetch-sources --fetch-host --out resources/rust-ise-db när det behövdes.
Falskpositiv-kontroll (fpc) — avstängd
Efter homology-träffar kan rust-ise köra fpc (false-positive control): nukleotidsökning mot fpc/refset för att märka träffar (fpFlag: IS, host, putative, …).

Det steget kraschade under WSL (mmseqs "search" failed i fp_control_module).

Workaround: bytte namn på mappen

resources/rust-ise-db/fpc → resources/rust-ise-db/fpc.bak

så att rust-ise hoppar över FP-steget. Homology-sökningen fungerade då. Utan fpc kan fler falska positiva komma med.
Snakemake-benchmark
Körde med ungefär:
Bashsnakemake -s workflow/Snakefile -c 2 \
  --config samples_tsv=config/samples_benchmark.tsv scanner=both use_ml=false

Filtrering av korta contigs + ISEScan + rust-ise på fyra genom.
Problem under dagen: PATH till rust-ise i Snakemake-jobb; skräp i out-mappar; use_ml från paths.yaml schemalade ML trots use_ml=false på kommandoraden tills yaml/regel styrdes om.

Jämförelsetabell (results/tables/scanner_compare.tsv), ungefärliga siffror:

sample		n_isescan	n_rustise	n_overlap	n_isescan_only	n_rustise_only
GCF_900489725v1	10		17		9		1		8
GCF_023035295v1	1		0		0		1		0
GCF_039783285v1	59		66		44		15		22
GCF_014335185v1	4		7		3		1		4

samplen_isescann_rustisen_overlapn_isescan_onlyn_rustise_onlyGCF_900489725v11017918GCF_023035295v110010GCF_039783285v15966441522GCF_014335185v147314
rust-ise rapporterade ofta fler partiala element och färre “complete” än ISEScan. Verktygen överlappar delvis men är inte identiska.
Disk full i WSL
Slut på utrymme under installation av stora paket.

WSL-disken (ext4.vhdx) hade redan Virtual size 1024 GB; Physical size ~12 GB = faktisk filstorlek på Windows. Behövde alltså inte expandera max — frigöra plats (conda clean, stora cachefiler) och se till att Windows C: har ledigt så vhdx kan växa. Två vhdx hittades under %LOCALAPPDATA%\wsl\; den större (~12,5 GB) är huvudinstallationen.
Maskininlärning (CNN) — miljö isescan-ml
Tims andra steg kräver egen conda-miljö med PyTorch (torch).

CUDA-hjul (~820 MB) avbröts upprepade gånger i pip → laddade ner med wget -c och installerade lokalt hjul.
Filnamn måste vara det fulla wheel-namnet (inte torch-cu128.whl).
Ytterligare NVIDIA-beroenden (t.ex. nvidia_cusparse_cu12) kunde också behöva wget.
CPU-torch är enklare om GPU inte syns i WSL.

Efter installation: use_ml: true och Snakemake. Första körningen kunde säga “Nothing to be done” om outputs redan fanns → rensa results/ml och kör om. ML-delen är experimentell (Tim: låg F1 på holdout).
Artikeln ISOSDB (läst som bakgrund)
Kirsch, Hryckowian & Duerkop 2024, Cell Host & Microbe: pipeline pseudoR + databas ISOSDB för IS-infogningar i metagenom. Annat lager än vår genom-annotation med ISEScan/rust-ise, men samma fenomen (IS-diversitet, accessory-gener, tarmmikrobiota).
Beslut / läge vid dagens slut

rust-ise fungerar för benchmark utan fpc.
scanner_compare.tsv finns.
Merge av PR:n är rimlig; dokumentera PATH, fpc under WSL, och att ML kräver isescan-ml.
Efter merge: valfri detektor via scanner=isescan|rust-ise|both och use_ml=true|false.
Plan: merge + frisk git clone i ny mapp för att testa som tredje person.

Påminnelser

Arbeta med export PATH="$HOME/.cargo/bin:$PATH" när rust-ise ska köras.
FPC_OFF = test -f resources/rust-ise-db/fpc/refset.dbtype ska faila (mappen bortflyttad).
Återaktivera fpc: mv .../fpc.bak .../fpc och testa; om panic → bygg om DB eller behåll avstängt.

2026-08-25 - Eget test av Tims pull request

Körde detta i nytt wsl-fönster:
cd ~
git clone https://github.com/Omnistudent/isescan-revisit.git isescan-revisit-fresh
cd isescan-revisit-fresh

# conda-miljö från repot
conda env create -f env/environment.yml
conda activate isescan-revisit

# rust-ise + DB (som Tim beskriver)
curl https://sh.rustup.rs -sSf | sh -s -- -y

source "$HOME/.cargo/env"
rustc --version
rustc 1.98.0 (88d9e12ae 2026-08-18)
cargo --version
cargo 1.98.0 (797e8a9bc 2026-08-05)

which mmseqs || conda install -c bioconda -c conda-forge mmseqs2 -y
/home/eris/miniconda3/envs/isescan-revisit/bin/mmseqs

bash scripts/setup_rustise.sh

which rust-ise
/home/eris/.cargo/bin/rust-ise

 snakemake -s workflow/Snakefile -c 2   --config samples_tsv=config/samples_benchmark.tsv scanner=both use_ml=false

Gav ett felmeddelande pga att det inte fanns några genom att analysera.

Löste detta med 
cd ~/isescan-revisit-fresh
conda activate isescan-revisit
mkdir -p data/raw

# om Tims/ditt download-skript finns:
ls config/ncbi_sample_benchmark.tsv config/samples_benchmark.tsv scripts/download*.py

python scripts/download_ncbi_sample.py \
  --samples config/ncbi_sample_benchmark.tsv \
  --outdir data/raw \
  --log results/logs/download_failures.log

2026-08-25 - Anpassar skripten för att kunna köras så "out of the box" som möjligt efter pull från github.

Ändrade rader i config/paths.yaml:

use_ml: false
scanner: isescan # eller rust-ise när setup_rustise.sh är körd

Lade till skriptet scripts/bootstrap.sh
Gör filen körbar: chmod +x scripts/bootstrap.sh.

Även setup_rustise.sh behöver göras körbar


## Snabbstart (ny klon)

```bash
git clone https://github.com/Omnistudent/isescan-revisit.git
cd isescan-revisit
conda env create -f env/environment.yml
conda activate isescan-revisit
bash scripts/bootstrap.sh
snakemake -s workflow/Snakefile -c 2 \
  --config samples_tsv=config/samples_benchmark.tsv scanner=isescan use_ml=false


Sedan en **kort** sektion “Tillval: rust-ise” med `setup_rustise.sh`, PATH och att fpc ofta måste av under WSL.

---

### 5. Vad som *inte* ska in i git  
Behåll i `.gitignore`: `data/raw/*.fna`, `results/isescan/`, `results/rust-ise/`, `resources/rust-ise-db/`, `.snakemake/`.  
Däremot **ska** dessa finnas: `config/samples_benchmark.tsv`, `config/ncbi_sample_benchmark.tsv`, tomma `data/raw/.gitkeep`.

---

### 6. Rimlig förväntan  
Efter det här tar en tredje person:

| Steg | Tid |
|---|---|
| conda env | 5–20 min |
| 4 genom via bootstrap | några minuter |
| ISEScan på 4 genom | tiotals minuter |
| rust-ise + DB | extra, och fpc kan behöva av |

Det är så nära “fungerar efter clone” ni kommer utan att checka in hundra MB genom och en IS-databas.

---

**Gör först:** `use_ml: false` + README-snabbstart + bootstrap som bara hämtar benchmark. Det var det som stoppade `isescan-revisit-fresh`. rust-ise-PATH/fpc är steg två.

Vill du att jag skriver ut hela `bootstrap.sh` och den nya README-toppen som färdiga filer att klistra in?



