#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
[[ -f "${ROOT}/config.env" ]] && source "${ROOT}/config.env"

LABEL="${1:?Usage: $0 GGE|FE|ALL}"
MAGMADIR="${MAGMADIR:-${ROOT}/tools/magma}"
MAGMA="${MAGMADIR}/bin/magma"
RESULTS="${ROOT}/results/${LABEL}"
PVAL="${MAGMADIR}/prepared/${LABEL}_magma.pval"
mkdir -p "$RESULTS"

[[ -x "$MAGMA" ]] || { echo "Run scripts/01 first; missing $MAGMA"; exit 1; }
[[ -f "$PVAL" ]] || { echo "Missing $PVAL — run 04_prepare_gwas_for_magma.py"; exit 1; }

G1000_BIM="$(find "${MAGMADIR}/ref" -name 'g1000_eur.bim' 2>/dev/null | head -1)"
[[ -n "$G1000_BIM" ]] || { echo "Missing g1000_eur reference. See 01 script / README."; exit 1; }
G1000="${G1000_BIM%.bim}"

find_annot() {
  find "${MAGMADIR}/annot" "${ROOT}/tools/magma/annot" -name "$1" 2>/dev/null | head -1
}

MAGMA_DEFAULT="$(find_annot 'MAGMA.genes.annot')"
EM_HIPPO="$(find_annot 'Brain_Hippocampus.genes.annot')"
H_ADULT="$(find_annot 'Adult_brain.genes.annot')"
H_FETAL="$(find_annot 'Fetal_brain.genes.annot')"
ME_ANNOT="${ME_MAGMA_ANNOT:-${MAGMADIR}/annot/me_magma.genes.annot}"

run_one() {
  local name="$1" annot="$2"
  [[ -f "$annot" ]] || { echo "Skip $name (missing $annot)"; return 0; }
  echo "=== $LABEL / $name ==="
  "$MAGMA" --bfile "$G1000" \
    --pval "$PVAL" ncol=3 \
    --gene-annot "$annot" \
    --out "${RESULTS}/${name}"
}

run_one "magma_default" "$MAGMA_DEFAULT"
run_one "emagma_hippocampus" "$EM_HIPPO"
run_one "hmagma_adult" "$H_ADULT"
run_one "hmagma_fetal" "$H_FETAL"
if [[ -f "$ME_ANNOT" ]]; then
  run_one "me_magma" "$ME_ANNOT"
else
  echo "ME-MAGMA: no annotation at $ME_ANNOT (run 06 after Schulz + manifest)"
fi

echo "Outputs in $RESULTS (*.genes.out)"
