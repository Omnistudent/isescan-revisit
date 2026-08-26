#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "1) conda-miljö"
conda env create -f env/environment.yml 2>/dev/null || true
# användaren aktiverar själv: conda activate isescan-revisit

echo "2) kataloger"
mkdir -p data/raw results/logs resources

echo "3) liten testdata (benchmark, inte 80 genom)"
if [[ ! -f data/raw/.benchmark_ok ]]; then
  python scripts/download_ncbi_sample.py \
    --samples config/ncbi_sample_benchmark.tsv \
    --outdir data/raw \
    --log results/logs/download_failures.log
  touch data/raw/.benchmark_ok
fi

echo "Klart. Aktivera miljön och kör:"
echo "  conda activate isescan-revisit"
echo "  snakemake -s workflow/Snakefile -c 2 \\"
echo "    --config samples_tsv=config/samples_benchmark.tsv scanner=isescan use_ml=false"