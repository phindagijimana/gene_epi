# Data and reference files acquired for this pipeline

Paths are under `mushunuri_ilae_pipeline/` unless noted.

## MAGMA European reference (`g1000_eur`)

- **Source:** [CNCR MAGMA page](https://cncr.nl/research/magma/) → Reference data → **European** (VU SURF Nextcloud).
- **Direct download used:** `https://vu.data.surfsara.nl/index.php/s/VZNByNwpD8qqINe/download` (~488 MB zip).
- **Installed files:** `tools/magma/ref/g1000_eur.{bed,bim,fam,synonyms}`, marker `tools/magma/ref/.g1000_eur_ready`.

Script `scripts/01_download_magma_and_reference.sh` now defaults to this URL when `g1000_eur.bim` is missing.

## H-MAGMA gene annotations (`*.genes.annot`)

- **Zenodo 6399470:** `data/raw/H-MAGMA-software.zip` (~340 MB) — extracted under `tools/magma/annot/hmagma/` (layout varies by zip).
- **Standardized copies** (stable paths for `05_run_magma_family.sh`): run **`scripts/normalize_hmagma_std.sh`** after `02`. It writes:
  - `tools/magma/annot/hmagma_std/MAGMA.genes.annot` (from `MAGMAdefault.genes.annot.gz` when present)
  - `tools/magma/annot/hmagma_std/Adult_brain.genes.annot`
  - `tools/magma/annot/hmagma_std/Fetal_brain.genes.annot`

## H-MAGMA protocol (optional extras)

- **Zenodo 6382668:** `data/raw/HMAGMA_Protocol_v1.02.zip` (~744 MB) — extracted to `tools/magma/annot/hmagma_protocol/` (tutorial / Rmd / alternate annotation formats).

## eMAGMA (hippocampus)

- **GitHub** `eskederks/eMAGMA-tutorial` branch `gtex_v8`, `emagma_annot_1.tar.gz`.
- **File:** `tools/magma/annot/emagma/Brain_Hippocampus.genes.annot`

## NCBI Entrez metadata

- **File:** `tools/magma/ref/Homo_sapiens.gene_info.gz` (for ME-MAGMA mapping).

## Illumina HumanMethylation450 manifest

- **GEO** [GPL13534](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL13534) supplementary:
  - `data/raw/GPL13534_HumanMethylation450_15017482_v.1.1.csv.gz`
  - Decompressed: `data/raw/GPL13534_HumanMethylation450_15017482_v1-1.csv`

## Schulz et al. 2017 (hippocampal meQTL) — Uni Bonn sciebo

Public WebDAV share (paper): `https://uni-bonn.sciebo.de/index.php/s/Nnj2o9GKCmZI2pn`

Downloaded under `data/raw/schulz2017/`:

| File | Role |
|------|------|
| `NatCommun_Schulz2017_readme.txt` | Short description |
| `NatCommun_Schulz2017_CpGLocation.zip` / `.txt` | CpG coordinates (hg19) |
| `NatCommun_Schulz2017_SNPLocation.zip` | SNP locations |
| `NatCommun_Schulz2017_ImputedSNPs_eQTLs.zip` | Imputed cis-eQTLs (expression probes) |
| `NatCommun_Schulz2017_ImputedSNPs_meQTLs.zip` | **Imputed cis-meQTLs** (~4.9 GB zip → ~29 GB `NatCommun_Schulz2017_ImputedSNPs_meQTLs.txt`) |

Springer **MOESM4** xlsx was **not** fetched (403 / HTML from automated clients). The **imputed meQTL table** from sciebo is used instead for ME-MAGMA-style SNP→CpG→gene mapping.

### ME-MAGMA annotation build

- **Script:** `scripts/10_stream_me_magma_from_schulz_imputed.py` (streaming, for large txt).
- **Default strictness:** `--max-p 1e-4` (tune to match your desired stringency; the paper’s supplementary table used FDR-based filtering on a **non-imputed** subset).
- **Output (when finished):** `tools/magma/annot/me_magma.genes.annot`
- **Log:** `data/raw/schulz2017/me_magma_build.log`

To rebuild with a different cutoff:

```bash
python3 scripts/10_stream_me_magma_from_schulz_imputed.py \
  --meqtl-zip data/raw/schulz2017/NatCommun_Schulz2017_ImputedSNPs_meQTLs.zip \
  --manifest data/raw/GPL13534_HumanMethylation450_15017482_v1-1.csv \
  --gene-info tools/magma/ref/Homo_sapiens.gene_info.gz \
  --max-p 5e-5 \
  --out tools/magma/annot/me_magma.genes.annot
```

The older `scripts/06_build_me_magma_annot.py` remains suitable for **small** MOESM4-style spreadsheets if you obtain the xlsx manually.
