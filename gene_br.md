# Builder Review — ILAE × MAGMA pipeline (Mushunuri et al. 2026 style)

Evaluation of the Epilepsia methods paper and this workspace’s **gene_epi** implementation, using the **Inzira Labs Builder Review** style (usability, reproducibility, performance, generalization, clinical use, interpretability, integration, limitations, builder conclusions). Full rubrics can live locally (Word/Markdown); they need not ship in a minimal repo.

**Primary reference:** Mushunuri et al. *Epilepsia* 2026. https://doi.org/10.1111/epi.70021

**Typical layout:** `mushunuri_ilae_pipeline/` (numbered scripts, `README.md`, `DATA_ACQUIRED.md`), parent **`./gene`** CLI (`install`, `start`, `stop`, `logs`, `checks`), state in `.gene/`; public downloads (EPIGAD, CNCR/VU MAGMA mirrors, Zenodo H-MAGMA, GitHub eMAGMA, Schulz sciebo meQTL, GEO GPL13534).

---

## Context

The paper describes **gene-level** dissection of epilepsy GWAS with **MAGMA**, **E-MAGMA** (hippocampal expression context), **H-MAGMA** (adult/fetal brain Hi-C context), and **ME-MAGMA** (methylation QTL linkage), on **ILAE** summary statistics. This workspace implements the **compute path** (reference LD panel, annotations, p-value prep, batch MAGMA) plus a thin **CLI**—not a re-implementation of MAGMA’s statistics.

---

## Platform fit and reproducibility

### Usability

**Published offering**

- Standard post-GWAS gene analysis stack; clear separation of summary stats vs. functional priors (expression, chromatin, methylation).

**This implementation**

- **Strength:** `./gene install` chains downloads + ILAE unzip + **three-column** p-value files; `./gene start` runs all phenotypes in background; `./gene checks` validates inputs and counts `*.genes.out`.
- **Friction:** **MAGMA v1.10** requires **SNP, P, N** in the p-value file (`ncol=3`); ILAE `.tbl` supplies `Effective_N`. Large **ILAE** zip (~1.8 GB) and **g1000_eur** (~488 MB) need bandwidth and disk.
- **ME-MAGMA:** Paper annotations not shared; builder uses **Schulz 2017** imputed meQTL + 450k manifest—**logic-aligned**, not byte-identical to authors’ file.

### Reproducibility

**What the paper supports**

- Public **ILAE3** sumstats (EPIGAD); public MAGMA/E-/H-MAGMA assets; fixed software versions when pinned.

**Gaps**

- **LD reference:** Paper used **ILAE2** European genotypes where available; pipeline defaults to **1000 Genomes EUR**—standard, but gene *p*-values can shift vs. ILAE2-LD.
- **ME-MAGMA:** Rebuilt annotation + *p*-cutoff choice (e.g. `1e-4`) affects inclusion; not a deterministic replay of undisclosed author files.
- **Our role:** Reproduces a **runnable, documented** pipeline—not independent re-validation of every gene claim in the paper.

---

## Performance, generalization, comparison

### Performance

- MAGMA gene tests over **~4.8M SNPs** and **~52k genes** are **CPU-heavy** (tens of minutes per annotation × multiple annotations × multiple phenotypes). **NFS** home latency can add overhead; local fast disk helps.
- This repo does **not** benchmark vs. paper wall times; `checks` only confirms **artifact presence**.

### Generalization

- GWAS summary format is **ILAE-specific** (column names, spacing); `04_prepare_gwas_for_magma.py` strips headers and maps `MarkerName` / `P-value` / `Effective_N`.
- Other cohorts need column detection tweaks or explicit `--input` conventions.
- **Clinical:** Gene lists are **research** outputs; not diagnostic or treatment directives.

### Comparison

- **E-MAGMA / H-MAGMA / ME-MAGMA** differ by **which SNPs count** toward each gene; same GWAS can yield different gene rankings. Builder should treat outputs as **complementary hypotheses**, not one “true” ranking.

---

## Clinical relevance, interpretability, integration

### Clinical relevance

- **Moderate–high** for research into **genetic architecture** of epilepsy subtypes (GGE vs focal vs all-epilepsy); supports pathway and follow-up variant interpretation.
- **Not** bedside validation, treatment selection, or regulatory evidence.

### Interpretability

- **`*.genes.out`:** gene ID, genomic interval, SNP count, **ZSTAT**, **P**. Lower **P** = stronger multi-SNP association under that annotation.
- **Trust limits:** LD panel, annotation build, and **winner’s curse** in GWAS summaries affect calibration; FDR (`08_fdr_genes.R`) is per-file, not cross-annotation unified.

### Integration

- **Downstream:** R/tidyverse for FDR; optional **VarElect** (external web); Entrez IDs link to external DBs.
- **`./gene`** adds **ops** (install/start/logs/stop/checks), not a lab LIMS or dbGaP connector.

---

## Limitations and failure modes

- **Network mirrors** (VU SURF, Zenodo, EPIGAD) can change; scripts pin URLs documented in `README.md` **Sources** table.
- **Headless clusters:** MAGMA is CLI-friendly; **no GUI** required—unlike LeGUI-style tools.
- **MAGMA version drift:** `ncol=2` + global `N=` conflicts on **v1.10**; pipeline standardizes **3-column** p-values.
- **Incomplete runs:** Partial `*.genes.out` set if batch interrupted; `./gene checks` expects **15** files (3 phenotypes × 5 annotations when ME annot exists).

---

## Builder insight

The stack is **strong for transparent, public-data gene follow-up** on ILAE GWAS with multiple functional priors. The **builder gap** is **harmonization**: choosing **LD reference**, accepting **ME-MAGMA** as a reproducible approximation, and budgeting **compute** for full annotation sweeps.

**Potential extensions**

- **Slurm** wrapper over `./gene start` with time/memory requests.
- **Config YAML** for phenotype file paths instead of hard-coded Caucasian `.tbl` names.
- **CI** job: `./gene checks` on a cache with tiny subset p-value file for smoke testing (not full GWAS).

---

## References (selected)

- Mushunuri et al. 2026 *Epilepsia* (DOI above).
- `gene_summary.md` — short paper summary in this folder.
- `mushunuri_ilae_pipeline/README.md` — install, sources, CLI.
- MAGMA: https://cncr.nl/research/magma/
- ILAE / EPIGAD: https://www.epigad.org/

Regenerate the Word handoff: `python3 export_builder_review_docx.py` → `build_reviewer.docx`.

---

*Last updated: 2026-04-15.*
