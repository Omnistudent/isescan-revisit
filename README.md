# ISEScan revisit

Modern omtagning av homology-baserad IS-detektion.

## Data

Rå FASTA ligger i sökvägen som anges i `config/paths.yaml` (`data_raw`).
Lägg till prover i `config/samples.tsv`.

## Kör

    conda env create -f env/environment.yml
    conda activate isescan-revisit
    snakemake -s workflow/Snakefile -c 2

## Anteckningar

Skriv beslut och resultatvägar i `notes/labbok.md`.
Spara inte misslyckade tester där.
