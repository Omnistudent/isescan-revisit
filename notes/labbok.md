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
Anteckning:Körde konda-kommando för att skapa miljö (och ladda ner saker)
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
password: test5bra

Resultat: installation lyckades, linux ligger i ().
conda --version misslyckades.


## 2026-08-20
Anteckning: Måste installera linux för att köra ISEScan
Anteckning: För att gå ur och komma tillbaks till ubuntu i powershell:
exit tar dig tillbaka till PowerShell.
Vill du ha Ubuntu igen: skriv wsl eller ubuntu i PowerShell.
Kommando: wsl --install från windows powershell som administratör

output i rutan: Create a default Unix user account: eris (jag valde eris och tryckte return)
password: test5bra

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
Startade isescan-revisit mijön för första gången
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
För att göra detta
Detta ledde till att ett fel hittades i /config/paths.yaml.

data_raw: /mnt/c/Users/Eris/data/isescan-revisit/raw

skall det stå för att nå raw-foldern från innuti ubuntu.
Kommando: snakemake --version
Resultat:9.24.0
Kommando: isescan.py --help
Resultat: hjälpfil printas