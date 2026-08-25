#!/usr/bin/env bash
# Installera rust-ise och bygg IS-profil-DB (ISOSDB ∪ ISfinder + FP-kontroll).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DB_DIR="${ISSCAN_DB:-$ROOT/resources/rust-ise-db}"

if ! command -v cargo >/dev/null 2>&1; then
  echo "cargo saknas. Installera Rust från https://rustup.rs" >&2
  exit 1
fi

if ! command -v rust-ise >/dev/null 2>&1; then
  echo "Kompilerar rust-ise..."
  cargo install --git https://github.com/necoli1822/rust-ise rust-ise
else
  echo "rust-ise finns redan: $(command -v rust-ise)"
fi

if ! command -v mmseqs >/dev/null 2>&1; then
  echo "mmseqs saknas på PATH. Aktivera conda-miljön isescan-revisit först." >&2
  exit 1
fi

if [[ ! -f "$DB_DIR/mmdb_union/profileDb.dbtype" ]]; then
  echo "Bygger IS-DB i $DB_DIR (första gången, några minuter)..."
  mkdir -p "$DB_DIR"
  rust-ise build-db --fetch-sources --fetch-host --out "$DB_DIR"
else
  echo "IS-DB finns redan i $DB_DIR"
fi

echo "Klart. rustise_db: $DB_DIR"
