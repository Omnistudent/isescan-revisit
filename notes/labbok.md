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
