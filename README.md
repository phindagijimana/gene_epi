# gene_epi

Computational workflow for **gene-level epilepsy GWAS analysis** using **MAGMA** and extensions (**E-MAGMA**, **H-MAGMA**, **ME-MAGMA**) on **ILAE** summary statistics, aligned with Mushunuri *et al.*, *Epilepsia* 2026 ([DOI 10.1111/epi.70021](https://doi.org/10.1111/epi.70021)).

## What’s in this repo

| Path | Purpose |
|------|---------|
| `gene` | CLI: install references, run MAGMA batch, logs, checks |
| `mushunuri_ilae_pipeline/` | Bash/Python/R scripts, `environment.yml`, `config.env.example` |
| `gene_summary.md` | Short narrative summary of the paper |
| `gene_br.md` | Structured notes (e.g. for reviews) |

Large or downloaded assets (`data/`, `tools/`, `results/`, local `config.env`) are **not** tracked; see `.gitignore`.

## Requirements

- Linux or WSL: `bash`, `curl`/`wget`, `unzip`, `tar`, **Python 3.10+**; **R 4.3+** optional (FDR helper)
- ~15 GB disk for sumstats + references
- Network access to CNCR/MAGMA mirrors, Zenodo, EPIGAD, etc.

## Quick start

```bash
git clone git@github.com:phindagijimana/gene_epi.git
cd gene_epi
chmod +x gene
./gene install   # downloads refs, ILAE sumstats, builds p-value files
./gene checks
./gene start     # background MAGMA for GGE, FE, ALL
./gene logs
```

Manual/script-only flow lives under `mushunuri_ilae_pipeline/scripts/`; see the guide below.

## Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** — full setup, data provenance, `g1000_eur` notes, ME-MAGMA build, outputs, citations
- **`mushunuri_ilae_pipeline/README.md`** — pointer into this repo’s docs
- **`mushunuri_ilae_pipeline/DATA_ACQUIRED.md`** — file-level paths for mirrored data

## Citation

Cite the Mushunuri *et al.* 2026 paper, MAGMA, E-MAGMA, H-MAGMA, ILAE GWAS, and Schulz *et al.* 2017 (meQTL source) as appropriate; details in [USER_GUIDE.md](USER_GUIDE.md).
