# Summary: Mushunuri et al. — Genetic risk in common epilepsies (integrative omics)

**Citation:** Mushunuri A, Adesoji O, Krause R, May P, Lerche H, Becker A, Grimm D, ILAE Consortium on Complex Epilepsies, Nothnagel M, Schulz H. *Genetic risk factor identification for common epilepsies guided by integrative omics data analysis.* **Epilepsia** 2026;67(3):1406–1420. DOI: [10.1111/epi.70021](https://doi.org/10.1111/epi.70021).

---

## One-sentence takeaway

The authors move beyond SNP-level GWAS by combining ILAE epilepsy summary statistics with **gene-level tests** that layer in **expression (eQTL)**, **3D chromatin contacts (Hi-C)**, and **DNA methylation (meQTL)** annotations—highlighting hundreds of **FDR-significant gene candidates** for genetic generalized epilepsy (GGE), with strongest biological stories around **ion channels**, **synaptic/transmembrane machinery**, and **epigenetic/regulatory** mechanisms.

---

## Problem and goal

- **Genetic generalized epilepsies (GGE)** are common and highly heritable but genetically complex; the large ILAE trans-ethnic GWAS already implicated many loci and plausible genes, yet the **full regulatory picture** (which genes are actually driven by risk variation through expression, chromatin looping, or methylation) remains incomplete.
- **Aim:** Identify genes whose **genetically regulated** expression (and related regulatory readouts) associates with epilepsy by integrating ILAE GWAS with **transcriptome-/epigenome-informed** gene mapping—not just “nearest gene” to a lead SNP.

---

## Methods (core ideas)

| Layer | Tool / data | Role |
|--------|-------------|------|
| **GWAS → genes (baseline)** | **MAGMA** on ILAE **third** meta-analysis (**ILAE3**; ~82k individuals; cases split into GGE, focal, all epilepsy) | Aggregates SNP association signal within genes; uses **ILAE2** European panel for LD reference. |
| **+ cis–eQTL (hippocampus)** | **E-MAGMA** (GTEx v8 hippocampus) | Maps risk variants to genes they likely **regulate via expression**. |
| **+ chromatin loops (adult vs fetal brain)** | **H-MAGMA** | Maps promoters/exonic SNPs to **long-range target genes**; fetal vs adult emphasizes **neurodevelopmental** regulation. |
| **+ meQTL (novel extension)** | **ME-MAGMA** (new; hippocampal **TLE** meQTLs + Illumina 450k CpG→gene links) | Links risk SNPs to genes through **methylation** intermediates—epigenetic angle on epileptogenesis-relevant tissue. |

- **Gene universe:** ~51,866 genes and **pseudogenes** (pseudogenes included given emerging noncoding/transcript evidence).
- **Significance:** Primary reporting uses **5% FDR** at gene level (exploratory multi-method overlaps); **Bonferroni** also reported for context.
- **Prioritization:** **VarElect** with phenotype keyword “epilepsy” to spotlight interpretable candidates from large lists.

---

## Main results (numbers that matter)

- **GGE:** **897** genes/pseudogenes pass **5% FDR** in the combined MAGMA-family analysis (per abstract and results narrative). **18** overlap genes previously implicated at SNP level in ILAE GWAS (e.g., *CACNA2D2*, *KCNIP2*, *SCN1A*, *SCN2A*, *RBFOX1*, *GABRA2*, *TMPRSS15*, etc.).
- **Cross-method overlap (GGE, FDR):** Illustrative counts from Venn-style summaries—**ME-MAGMA** ~58, **E-MAGMA** ~28, **H-MAGMA Adult** ~85, **H-MAGMA Fetal** ~164 genes (exact overlap sets in supplement). Only **DPM2** and **VAMP2** appear across **all five** MAGMA-family analyses at that threshold; **VAMP2** was the one of those previously noted in the original ILAE study.
- **Focal epilepsy:** Fewer robust gene hits; **three** genes **not** reported in prior ILAE GWAS summaries stand out: **FANCD2P2**, **CUL4A** (MAGMA), **PROZ** (ME-MAGMA + E-MAGMA).
- **All epilepsy:** **97** FDR genes; **five** were already recognized in earlier ILAE work (*KCNIP2*, *RMI1*, *SCN1A*, *FANCL*, *SPOCK1*; *ARHGEF15* also noted in related comparisons).

**Regional pattern:** Strong clustering of top methylation- and eQTL-informed signals on **chromosomes 3** (notably **3p21.31**) and **17**—interpreted as possible **regulatory hotspots** for GGE.

---

## Biological themes (genes and pathways)

1. **Voltage-gated calcium channels (VGCCs)**  
   - **CACNA2D2** (α2δ2): reinforces prior GGE / developmental–epileptic encephalopathy links.  
   - **CACNB2** (β2): novel for GGE in this framing; discussed alongside broader calcium-channel dysregulation in epilepsy.

2. **Potassium channels**  
   - **KCNT1**, **KCND3**, **KCNJ4**: highlighted as **new** GGE associations in this integrative setting, while connecting to known severe **monogenic** or related epilepsy phenotypes—suggesting **common variants** may modulate GGE risk in the same biological modules.  
   - **KCNIP2**, **KCNN2**: consistency with prior ILAE candidate genes.

3. **mTOR / nutrient-sensing and related regulators**  
   - **NPRL2** (strong ME-MAGMA signal): discussed as linking **FE** associations to possible **GGE** mechanisms via shared regulatory logic (**mTORC1** / sodium channel expression context in cited work).

4. **Transmembrane and trafficking genes**  
   - **TMEM** family members (**TMEM107**, **TMEM177**, **TMEM115**, **TMEM186**) and **VAMP2** (robust cross-method hit): point to **membrane biology, vesicle fusion, ciliary/mitochondrial** contexts that align with developmental epilepsy syndromes.

5. **Transcriptional regulators**  
   - **Zinc finger** genes (**ZBTB32**, **ZNF668**, **ZNF629**) tie risk to **chromatin-level** control—consistent with the paper’s multi-omic emphasis.

6. **Development**  
   - **Fetal vs adult H-MAGMA** is used explicitly to argue that some associations may reflect **early brain wiring** rather than only adult neuronal physiology.

---

## Strengths and caveats (as framed in the paper)

- **Strength:** Coherent **multi-layer** mapping (position + expression + chromatin + methylation) reduces reliance on arbitrary SNP-to-gene rules and generates **testable** regulatory hypotheses.
- **Caveat:** **ME-MAGMA** methylation annotations come from **TLE hippocampus**—informative for regulatory activity in epileptic tissue but **not** a matched GGE tissue model; authors argue this is acceptable for **annotation** (not phenotype definition) but interpret shared vs distinct mechanisms carefully.
- **Caveat:** Gene-level FDR across **many correlated tests and methods** is **exploratory**; follow-up needs **functional validation**, rare-variant convergence, and cell-type–specific data.

---

## Why it matters for “gene-level” epilepsy research

The study **expands the catalog** of statistically prioritized genes for **GGE** beyond the usual GWAS “nearest gene” list, emphasizes **ion channel and synaptic** biology consistent with known epilepsy mechanisms, and introduces **ME-MAGMA** as a template for weaving **epigenetic QTL** information into **MAGMA-style** gene discovery—potentially pointing toward **new targets** or biomarker hypotheses for common epilepsies.
