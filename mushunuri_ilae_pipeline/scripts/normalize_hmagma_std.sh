#!/usr/bin/env bash
# After 02_download_emagma_hmagma_assets.sh, ensure stable paths under annot/hmagma_std/
# so find_annot 'MAGMA.genes.annot' succeeds (zip often ships MAGMAdefault.genes.annot.gz).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
[[ -f "${ROOT}/config.env" ]] && source "${ROOT}/config.env"
MAGMADIR="${MAGMADIR:-${ROOT}/tools/magma}"
STD="${MAGMADIR}/annot/hmagma_std"
mkdir -p "$STD"

if [[ ! -f "${STD}/MAGMA.genes.annot" ]]; then
  z="$(find "${MAGMADIR}/annot" -name 'MAGMAdefault.genes.annot.gz' 2>/dev/null | head -1)"
  if [[ -n "$z" ]]; then
    echo "Decompressing $z -> ${STD}/MAGMA.genes.annot"
    gzip -dc "$z" >"${STD}/MAGMA.genes.annot"
  else
    p="$(find "${MAGMADIR}/annot" \( -name 'MAGMA.genes.annot' -o -name 'MAGMAdefault.genes.annot' \) ! -path '*/hmagma_std/*' 2>/dev/null | head -1)"
    if [[ -n "$p" ]]; then
      cp -f "$p" "${STD}/MAGMA.genes.annot"
    fi
  fi
fi

for f in Adult_brain.genes.annot Fetal_brain.genes.annot; do
  if [[ ! -f "${STD}/${f}" ]]; then
    src="$(find "${MAGMADIR}/annot" -name "$f" 2>/dev/null | head -1)"
    if [[ -n "$src" ]]; then
      echo "Copy $src -> ${STD}/${f}"
      cp -f "$src" "${STD}/${f}"
    fi
  fi
done

[[ -f "${STD}/MAGMA.genes.annot" ]] || echo "WARNING: ${STD}/MAGMA.genes.annot still missing — check H-MAGMA zip layout." >&2
ls -la "$STD" 2>/dev/null || true
