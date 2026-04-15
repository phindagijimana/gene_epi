#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
[[ -f "${ROOT}/config.env" ]] && source "${ROOT}/config.env"
MAGMADIR="${MAGMADIR:-${ROOT}/tools/magma}"
mkdir -p "${MAGMADIR}/annot/emagma" "${MAGMADIR}/annot/hmagma"

EMAGMA_TGZ="https://raw.githubusercontent.com/eskederks/eMAGMA-tutorial/gtex_v8/emagma_annot_1.tar.gz"
if [[ ! -f "${MAGMADIR}/annot/emagma/.complete" ]]; then
  echo "Downloading eMAGMA annotation tarball (GTEx v8; includes Brain_Hippocampus)"
  tmp="$(mktemp)"
  curl -fsSL -o "$tmp" "$EMAGMA_TGZ"
  tar -xzf "$tmp" -C "${MAGMADIR}/annot/emagma"
  rm -f "$tmp"
  touch "${MAGMADIR}/annot/emagma/.complete"
fi

HMAGMA_ZIP_URL="${HMAGMA_ZIP_URL:-https://zenodo.org/records/6399470/files/thewonlab/H-MAGMA-software.zip?download=1}"
if [[ ! -f "${MAGMADIR}/annot/hmagma/.complete" ]]; then
  echo "Downloading H-MAGMA software archive from Zenodo"
  tmp="$(mktemp)"
  curl -fsSL -o "$tmp" "$HMAGMA_ZIP_URL"
  unzip -o "$tmp" -d "${MAGMADIR}/annot/hmagma"
  rm -f "$tmp"
  touch "${MAGMADIR}/annot/hmagma/.complete"
fi

echo "eMAGMA annot search: find ${MAGMADIR}/annot/emagma -name 'Brain_Hippocampus.genes.annot'"
echo "H-MAGMA annot search: find ${MAGMADIR}/annot/hmagma -name 'Adult_brain.genes.annot' -o -name 'Fetal_brain.genes.annot'"
