En gång
Bashconda env create -f env/environment.yml

Lägg FASTA i data_raw, uppdatera config/samples.tsv.

Varje ny terminal
Bashconda activate isescan-revisit

Varje körning
Bashsnakemake -s workflow/Snakefile -n      # testa
snakemake -s workflow/Snakefile -c 4    # kör