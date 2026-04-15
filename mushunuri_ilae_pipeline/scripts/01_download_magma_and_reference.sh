#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
[[ -f "${ROOT}/config.env" ]] && source "${ROOT}/config.env"
MAGMADIR="${MAGMADIR:-${ROOT}/tools/magma}"
REFDIR="${MAGMADIR}/ref"
mkdir -p "${MAGMADIR}/bin" "${REFDIR}" "${MAGMADIR}/annot" "${MAGMADIR}/prepared"

# VU SURF mirror (CTG URLs often return HTML outside the VU network)
VU_MAGMA_SHARE="https://vu.data.surfsara.nl/index.php/s/lxDgt2dNdNr6DYt/download?path=%2F&files="
VU_NCBI37_SHARE="https://vu.data.surfsara.nl/index.php/s/Pj2orwuF2JYyKxq/download"
MAGMA_ZIP_URL="${MAGMA_ZIP_URL:-${VU_MAGMA_SHARE}magma_v1.08_static.zip}"
# Gene locations (build 37) live on a separate CNCR/VU share — not under the MAGMA program zip folder
NCBI37_ZIP_URL="${NCBI37_ZIP_URL:-$VU_NCBI37_SHARE}"

is_zip() {
  [[ -f "$1" ]] && file "$1" | grep -qi 'zip archive'
}

fetch_zip() {
  local url="$1" out="$2"
  echo "Downloading $(basename "$out")"
  tmp="$(mktemp)"
  curl -fsSL -o "$tmp" "$url"
  if ! is_zip "$tmp"; then
    echo "ERROR: $(basename "$out") download is not a zip (wrong URL or HTML error page). URL: $url" >&2
    rm -f "$tmp"
    return 1
  fi
  mv "$tmp" "$out"
}

if [[ ! -x "${MAGMADIR}/bin/magma" ]]; then
  fetch_zip "$MAGMA_ZIP_URL" "${MAGMADIR}/bin/magma_dist.zip"
  unzip -o "${MAGMADIR}/bin/magma_dist.zip" -d "${MAGMADIR}/bin"
  rm -f "${MAGMADIR}/bin/magma_dist.zip"
  if [[ ! -f "${MAGMADIR}/bin/magma" ]]; then
    M="$(find "${MAGMADIR}/bin" -maxdepth 3 -name 'magma' -type f | head -1)"
    [[ -n "$M" ]] || { echo "Could not find magma binary after unzip"; exit 1; }
    mv "$M" "${MAGMADIR}/bin/magma"
  fi
  chmod +x "${MAGMADIR}/bin/magma"
fi

if [[ ! -f "${REFDIR}/.ncbi37_unzipped" ]]; then
  fetch_zip "$NCBI37_ZIP_URL" "${REFDIR}/NCBI37.3.zip"
  unzip -o "${REFDIR}/NCBI37.3.zip" -d "${REFDIR}"
  touch "${REFDIR}/.ncbi37_unzipped"
fi

# 1000 Genomes EUR PLINK prefix (hg19) — required for --bfile
# Official mirror (CNCR MAGMA page, “European”, ~488 MB): VU SURF Nextcloud
G1000_EUR_DEFAULT_URL="${G1000_EUR_DEFAULT_URL:-https://vu.data.surfsara.nl/index.php/s/VZNByNwpD8qqINe/download}"
G1000_MARKER="${REFDIR}/.g1000_eur_ready"
if [[ ! -f "$G1000_MARKER" ]]; then
  if [[ -f "${REFDIR}/g1000_eur.bim" ]]; then
    touch "$G1000_MARKER"
  elif [[ -n "${G1000_EUR_ZIP_URL:-}" ]]; then
    fetch_zip "$G1000_EUR_ZIP_URL" "${REFDIR}/g1000_eur.zip"
    unzip -o "${REFDIR}/g1000_eur.zip" -d "${REFDIR}"
    touch "$G1000_MARKER"
  elif [[ -f "${REFDIR}/g1000_eur.zip" ]]; then
    unzip -o "${REFDIR}/g1000_eur.zip" -d "${REFDIR}"
    touch "$G1000_MARKER"
  else
    echo "Fetching g1000_eur.zip from VU SURF (European reference, ~488 MB) ..."
    if fetch_zip "$G1000_EUR_DEFAULT_URL" "${REFDIR}/g1000_eur.zip"; then
      unzip -o "${REFDIR}/g1000_eur.zip" -d "${REFDIR}"
      touch "$G1000_MARKER"
    else
      cat <<EOF >&2
[!] Automatic g1000_eur download failed. Install manually:
    https://cncr.nl/research/magma/ → Reference data → European → save as:
    ${REFDIR}/g1000_eur.zip
    Then re-run this script.
EOF
    fi
  fi
fi

if [[ ! -f "${REFDIR}/Homo_sapiens.gene_info.gz" ]]; then
  curl -fsSL -o "${REFDIR}/Homo_sapiens.gene_info.gz" \
    "https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz"
fi

echo "MAGMA: ${MAGMADIR}/bin/magma"
"${MAGMADIR}/bin/magma" --version || true
if [[ -f "$G1000_MARKER" ]]; then
  echo "g1000 EUR: $(find "${REFDIR}" -name 'g1000_eur.bim' | head -1)"
fi
