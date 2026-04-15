#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
chmod +x scripts/*.sh scripts/*.py 2>/dev/null || true
[[ -f config.env ]] || { cp config.env.example config.env && echo "Created config.env"; }
# shellcheck source=/dev/null
source config.env

./scripts/01_download_magma_and_reference.sh
./scripts/02_download_emagma_hmagma_assets.sh
./scripts/normalize_hmagma_std.sh
./scripts/03_download_ilae_sumstats.sh

PREP="${MAGMADIR:-${ROOT}/tools/magma}/prepared"
export ILAE_DEFAULT_N="${ILAE_DEFAULT_N:-82500}"
for spec in \
  "GGE:data/ilae3_sumstats/ILAE3_Caucasian_GGE_final.tbl" \
  "FE:data/ilae3_sumstats/ILAE3_Caucasian_focal_epilepsy_final.tbl" \
  "ALL:data/ilae3_sumstats/ILAE3_Caucasian_all_epilepsy_final.tbl"; do
  L="${spec%%:*}"
  F="${spec#*:}"
  [[ -f "$ROOT/$F" ]] || { echo "Skip $L — missing $F"; continue; }
  python3 scripts/04_prepare_gwas_for_magma.py --input "$ROOT/$F" --label "$L" --out-dir "$PREP"
done

echo "Data + p-value prep done. Run MAGMA (long): ./scripts/05_run_magma_family.sh GGE  (then FE, ALL)"
echo "Or from gene_epi: ../gene start"
