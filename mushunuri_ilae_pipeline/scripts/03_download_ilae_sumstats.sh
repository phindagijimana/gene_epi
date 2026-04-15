#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
[[ -f "${ROOT}/config.env" ]] && source "${ROOT}/config.env"
DEST="${ILAE_SUMSTATS_DIR:-${ROOT}/data/ilae3_sumstats}"
mkdir -p "${ROOT}/data/raw"

ZIP_URL="${ILAE3_SUMSTATS_URL:-http://www.epigad.org/download/final_sumstats.zip}"
ZIP_LOCAL="${ROOT}/data/raw/final_sumstats.zip"

if [[ ! -f "$ZIP_LOCAL" ]]; then
  echo "Downloading ILAE3 summary statistics (~1.8 GB) to $ZIP_LOCAL"
  curl -fSL -o "$ZIP_LOCAL" "$ZIP_URL"
else
  echo "Using existing $ZIP_LOCAL"
fi

mkdir -p "$DEST"
echo "Unpacking into $DEST (this may take several minutes)"
unzip -o "$ZIP_LOCAL" -d "$DEST"
echo "Done. Set ILAE_SUMSTATS_DIR=$DEST in config.env and run 04_prepare_gwas_for_magma.py --discover"
