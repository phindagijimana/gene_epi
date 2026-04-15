# User guide: ILAE × MAGMA pipeline (Mushunuri et al. 2026 style)

This document describes the **computational workflow** in *Mushunuri et al., Epilepsia 2026* (DOI [10.1111/epi.70021](https://doi.org/10.1111/epi.70021)): gene-level tests using **MAGMA**, **E-MAGMA** (hippocampal eQTL), **H-MAGMA** (adult + fetal Hi-C), and **ME-MAGMA** (meQTL → CpG → gene), applied to **ILAE** GWAS summary statistics.

Repository overview: [README.md](README.md).

## What you get vs. exact replication

| Piece | Status |
|--------|--------|
| **ILAE3 summary statistics** | Public: [epigad.org `final_sumstats.zip`](http://www.epigad.org/download/final_sumstats.zip) (~1.8 GB). |
| **LD reference** | Paper uses **ILAE2** European PLINK genotypes (consortium); those **may not be public**. This pipeline defaults to **1000 Genomes EUR** from the [MAGMA reference bundle](https://ctg.cncr.nl/software/magma) (`g1000_eur`), which matches common practice and H-MAGMA docs. Swap in ILAE2 if you obtain it. |
| **MAGMA / E-MAGMA / H-MAGMA** | Fully automatable with public binaries and annotation files. |
| **ME-MAGMA** | Authors did not share annotation files. This repo includes a **builder** that reproduces their *logic* using **Schulz et al. 2017** hippocampal cis-meQTL supplementary data + Illumina 450k probe→gene mapping. You must **download** the supplementary table manually (Nature / journal CDNs often block bots). |
| **VarElect prioritization** | Not scripted (web tool); optional downstream. |
| **Numerical identity** | Using `g1000_eur` instead of ILAE2 and rebuilt ME-MAGMA annotations may shift gene *p*-values slightly vs. the paper. |

## Sources for each implementation piece

This table is the **provenance map**: where each part of the workflow comes from, how it enters the repo, and which script installs or builds it. Mirrors and filenames can change; the **canonical landing pages** are listed first.

| Element | Role in this repo | Primary source (canonical) | How it is obtained here |
|--------|-------------------|----------------------------|-------------------------|
| **Paper workflow** | Phenotypes (GGE / focal / all-epilepsy), MAGMA family, interpretation | Mushunuri et al., *Epilepsia* 2026, [DOI 10.1111/epi.70021](https://doi.org/10.1111/epi.70021) | Not downloaded; cited for methods alignment |
| **MAGMA binary** | `tools/magma/bin/magma` — gene/SNP-level analysis | [CNCR MAGMA / program downloads](https://cncr.nl/research/magma/) | `scripts/01_download_magma_and_reference.sh` — static Linux build from VU SURF: `https://vu.data.surfsara.nl/index.php/s/lxDgt2dNdNr6DYt/download?path=%2F&files=magma_v1.08_static.zip` (zip may ship **v1.10** binary; both work with `ncol=3` p-value files) |
| **NCBI build 37 gene locations** | `NCBI37.3.gene.loc` under `tools/magma/ref/` — MAGMA/auxiliary gene coordinate file | [CNCR MAGMA → Auxiliary → Gene locations build 37](https://cncr.nl/research/magma/) | `scripts/01_download_magma_and_reference.sh` — `https://vu.data.surfsara.nl/index.php/s/Pj2orwuF2JYyKxq/download` |
| **1000 Genomes EUR (LD reference)** | `g1000_eur.{bed,bim,fam}` (+ synonyms) — SNP LD for `--bfile` | [CNCR MAGMA → Reference data → European](https://cncr.nl/research/magma/) | `scripts/01_download_magma_and_reference.sh` — default `https://vu.data.surfsara.nl/index.php/s/VZNByNwpD8qqINe/download` (~488 MB zip) |
| **NCBI Entrez gene info** | `Homo_sapiens.gene_info.gz` — symbol → Entrez for ME-MAGMA builders | NCBI Gene FTP: [Homo_sapiens.gene_info.gz](https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz) | `scripts/01_download_magma_and_reference.sh` (`curl` to NCBI) |
| **ILAE3 GWAS summary statistics** | `data/ilae3_sumstats/*.tbl` (after unzip) — SNP *P*, `Effective_N`, etc. | [EPIGAD](https://www.epigad.org/) — release file `final_sumstats.zip` | `scripts/03_download_ilae_sumstats.sh` — `http://www.epigad.org/download/final_sumstats.zip` → unzip to `ILAE_SUMSTATS_DIR` |
| **Prepared MAGMA p-value input** | `tools/magma/prepared/<LABEL>_magma.pval` — SNP, *P*, per-SNP *N* (MAGMA **v1.10** requires **3 columns**, `ncol=3`) | Derived from ILAE `.tbl` above | `scripts/04_prepare_gwas_for_magma.py` |
| **Default MAGMA gene annotation** | `tools/magma/annot/hmagma_std/MAGMA.genes.annot` | Bundled with **H-MAGMA software** archive (Zenodo) | `scripts/02_download_emagma_hmagma_assets.sh` then `scripts/normalize_hmagma_std.sh` (decompress / copy defaults); see `mushunuri_ilae_pipeline/DATA_ACQUIRED.md` |
| **E-MAGMA (hippocampus)** | `tools/magma/annot/emagma/Brain_Hippocampus.genes.annot` | [eMAGMA-tutorial (GTEx v8)](https://github.com/eskederks/eMAGMA-tutorial) — branch `gtex_v8`, file `emagma_annot_1.tar.gz` | `scripts/02_download_emagma_hmagma_assets.sh` — `https://raw.githubusercontent.com/eskederks/eMAGMA-tutorial/gtex_v8/emagma_annot_1.tar.gz` |
| **H-MAGMA (adult / fetal brain)** | `Adult_brain.genes.annot`, `Fetal_brain.genes.annot` (under `hmagma_std/` or extracted tree) | **Zenodo** record for H-MAGMA software: [doi:10.5281/zenodo.6399470](https://doi.org/10.5281/zenodo.6399470), file `thewonlab/H-MAGMA-software.zip` | `scripts/02_download_emagma_hmagma_assets.sh` — `https://zenodo.org/records/6399470/files/thewonlab/H-MAGMA-software.zip?download=1` |
| **H-MAGMA protocol extras (optional)** | Tutorial / alternate formats under `tools/magma/annot/hmagma_protocol/` | [Zenodo 6382668](https://doi.org/10.5281/zenodo.6382668) (`HMAGMA_Protocol_v1.02.zip`) | Manual download / unpack; documented in `mushunuri_ilae_pipeline/DATA_ACQUIRED.md` |
| **Illumina 450k manifest** | Probe → gene (UCSC RefGene) for ME-MAGMA-style mapping | GEO platform [GPL13534](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL13534) supplementary CSV | Manual or scripted fetch → `data/raw/GPL13534_*` (see `mushunuri_ilae_pipeline/DATA_ACQUIRED.md`) |
| **Schulz et al. 2017 hippocampal meQTLs** | Imputed cis-meQTL table (zip → large `.txt`) for SNP→CpG→gene | Schulz *et al.*, *Nat Commun* 2017 — data share: `https://uni-bonn.sciebo.de/index.php/s/Nnj2o9GKCmZI2pn` | Download bundles under `data/raw/schulz2017/`; **MOESM4** spreadsheet from the journal was not used (automated fetch often blocked) |
| **ME-MAGMA-style annotation file** | `tools/magma/annot/me_magma.genes.annot` | **Built locally** from Schulz meQTL + GPL13534 + `Homo_sapiens.gene_info.gz` (not the paper’s unreleased ME-MAGMA drop) | `scripts/10_stream_me_magma_from_schulz_imputed.py` (large table) or `scripts/06_build_me_magma_annot.py` (small table/xlsx) |
| **Gene-level outputs** | `results/<GGE|FE|ALL>/*.genes.out` | **Produced by MAGMA** using inputs above | `scripts/05_run_magma_family.sh` |
| **FDR helper (optional)** | R post-processing of `*.genes.out` | No external data | `scripts/08_fdr_genes.R` |
| **VarElect (optional)** | Gene prioritization UI | [VarElect](https://velect.medgen.med.uth.gr/) (web tool; not bundled) | Manual; not scripted |

For **file-level paths** already mirrored in a local workspace, see **`mushunuri_ilae_pipeline/DATA_ACQUIRED.md`**.

## Prerequisites

- **Linux** (or WSL) with `bash`, `curl`/`wget`, `unzip`, `tar`, **Python 3.10+**, **R 4.3+** (optional, for FDR helper).
- **~15 GB** free disk space (sumstats zip + references + annotations).
- Network access to CTG CNCR, GitHub, Zenodo, EPIGAD.

## Quick start

**One-shot from the repository root** (`gene_epi/`), using the `gene` CLI:

```bash
cd gene_epi
chmod +x gene
./gene install    # downloads refs, ILAE, builds GGE/FE/ALL p-value files (conda env optional)
./gene checks     # verify inputs
./gene start      # background: MAGMA for GGE, FE, ALL (15 runs)
./gene logs       # tail the batch log
./gene stop       # stop batch + MAGMA children
```

**Manual steps** (same as `install` + `start`):

```bash
cd mushunuri_ilae_pipeline
chmod +x scripts/*.sh scripts/*.py
cp config.env.example config.env
source config.env

./scripts/01_download_magma_and_reference.sh   # MAGMA + NCBI37.3 from VU mirror; see g1000 note below
./scripts/02_download_emagma_hmagma_assets.sh  # eMAGMA + H-MAGMA Zenodo archive
./scripts/normalize_hmagma_std.sh              # MAGMA.genes.annot + adult/fetal under hmagma_std/

# ILAE3 (~1.8 GB):
./scripts/03_download_ilae_sumstats.sh

source config.env
./scripts/04_prepare_gwas_for_magma.py --discover   # optional: list files
# Caucasian ILAE3 tables used by the CLI:
./scripts/04_prepare_gwas_for_magma.py --input "data/ilae3_sumstats/ILAE3_Caucasian_GGE_final.tbl" --out-dir "${MAGMADIR}/prepared" --label GGE
# Repeat with FE / ALL and ILAE3_Caucasian_focal_epilepsy_final.tbl / ILAE3_Caucasian_all_epilepsy_final.tbl

./scripts/05_run_magma_family.sh GGE
./scripts/05_run_magma_family.sh FE
./scripts/05_run_magma_family.sh ALL
```

Or run **`./scripts/run_all.sh`** inside `mushunuri_ilae_pipeline` through p-value preparation (no MAGMA):  
`cd mushunuri_ilae_pipeline && ./scripts/run_all.sh`

### `g1000_eur` reference (important)

Script `01` installs **MAGMA** and **NCBI37.3** via the VU SURF mirror. The **1000 Genomes EUR** PLINK bundle (`g1000_eur.bed/.bim/.fam`) is **not** always available from the same mirror. If `01` warns about missing `g1000_eur`, download **`g1000_eur.zip`** from the [official MAGMA / CTG reference page](https://ctg.cncr.nl/software/magma) in a browser, save it as `${MAGMADIR}/ref/g1000_eur.zip`, and run `01` again (it will only unzip).

### Gene annotation files

After `02`, run **`./scripts/normalize_hmagma_std.sh`** so `MAGMA.genes.annot` and adult/fetal Hi-C annots live under `tools/magma/annot/hmagma_std/` (the Zenodo zip often ships `MAGMAdefault.genes.annot.gz` instead).

You can still locate files anywhere under `annot/` with:

```bash
find tools/magma/annot -name 'Brain_Hippocampus.genes.annot'
find tools/magma/annot -name 'MAGMA.genes.annot'
find tools/magma/annot -name 'Adult_brain.genes.annot'
```

If annots are missing from the Zenodo **software** archive, download the **H-MAGMA Protocol** bundle from [Zenodo 6382668](https://doi.org/10.5281/zenodo.6382668), unzip under `tools/magma/annot/hmagma/`, then re-run **`normalize_hmagma_std.sh`**.

## ME-MAGMA annotation

See **`mushunuri_ilae_pipeline/DATA_ACQUIRED.md`** for what was downloaded into a local workspace (sciebo meQTL zip, 450k manifest, etc.).

**Recommended (large imputed meQTL table, streaming):**

```bash
cd mushunuri_ilae_pipeline
python3 scripts/10_stream_me_magma_from_schulz_imputed.py \
  --meqtl-zip data/raw/schulz2017/NatCommun_Schulz2017_ImputedSNPs_meQTLs.zip \
  --manifest data/raw/GPL13534_HumanMethylation450_15017482_v1-1.csv \
  --gene-info tools/magma/ref/Homo_sapiens.gene_info.gz \
  --max-p 1e-4 \
  --out tools/magma/annot/me_magma.genes.annot
```

Adjust `--max-p` for stricter or looser inclusion (the Mushunuri pipeline used FDR-filtered **non-imputed** meQTLs; the imputed file needs an explicit *p*-value cutoff).

**Alternative (small spreadsheet):** if you obtain **MOESM4** / Supplementary Data 1 as `.xlsx` or `.csv`, use `scripts/06_build_me_magma_annot.py` as before.

`05_run_magma_family.sh` picks up `tools/magma/annot/me_magma.genes.annot` automatically when present.

## Outputs

Under `results/<PHENOTYPE>/` you will find `*.genes.out` (gene-level statistics) for:

- `magma_default`
- `emagma_hippocampus`
- `hmagma_adult`
- `hmagma_fetal`
- `me_magma` (after annotation build)

Use `scripts/08_fdr_genes.R` (optional) to apply Benjamini–Hochberg FDR 5% per output.

## References (tools)

- MAGMA: [cncr.nl/research/magma](https://cncr.nl/research/magma)
- E-MAGMA tutorial (GTEx v8 annot): [github.com/eskederks/eMAGMA-tutorial](https://github.com/eskederks/eMAGMA-tutorial) (branch `gtex_v8`)
- H-MAGMA software + inputs: [Zenodo 6399470](https://doi.org/10.5281/zenodo.6399470)
- ILAE GWAS: [epigad.org](https://www.epigad.org/)
- Schulz 2017 meQTL share: [uni-bonn.sciebo.de/…/Nnj2o9GKCmZI2pn](https://uni-bonn.sciebo.de/index.php/s/Nnj2o9GKCmZI2pn)

## Citation

If you use this pipeline, cite the original paper (Mushunuri et al. 2026), MAGMA, E-MAGMA, H-MAGMA, ILAE consortium GWAS, and Schulz et al. 2017 for meQTL source data.
