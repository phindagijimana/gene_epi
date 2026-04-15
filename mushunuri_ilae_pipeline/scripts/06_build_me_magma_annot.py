#!/usr/bin/env python3
"""
Build a MAGMA --gene-annot file from hippocampal cis-meQTL summary data (Schulz et al. style)
by mapping SNP → CpG → nearest gene on the Illumina 450k manifest, then Entrez IDs.

Output format (per line): ENTREZ_ID rs123 rs456 ...
This matches H-MAGMA / MAGMA multi-SNP gene annotation conventions.
"""
from __future__ import annotations

import argparse
import gzip
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd


def load_gene_info(path: str) -> dict[str, str]:
    """symbol -> Entrez (prefer protein-coding)."""
    sym_to_entrez: dict[str, str] = {}
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", errors="replace") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 3:
                continue
            tax, entrez, sym = parts[0], parts[1], parts[2]
            if tax != "9606" or sym == "-" or not sym:
                continue
            sym_to_entrez[sym.upper()] = entrez
    return sym_to_entrez


def detect_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cmap = {c.upper().replace(" ", "_"): c for c in df.columns}
    for cand in candidates:
        if cand in cmap:
            return cmap[cand]
    for c in df.columns:
        u = c.upper()
        for cand in candidates:
            if cand in u:
                return c
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description="ME-MAGMA-style SNP→gene MAGMA annotation")
    ap.add_argument("--meqtl", required=True, help="Schulz 2017 supplementary meQTL table (.csv/.txt/.xlsx)")
    ap.add_argument("--manifest", required=True, help="Illumina 450k manifest with probe ID + gene column")
    ap.add_argument("--gene-info", required=True, help="Homo_sapiens.gene_info.gz from NCBI")
    ap.add_argument("--out", required=True, help="Output .genes.annot path")
    args = ap.parse_args()

    sym_to_e = load_gene_info(args.gene_info)

    mepath = Path(args.meqtl)
    if mepath.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(mepath, dtype=str)
    else:
        df = pd.read_csv(mepath, sep=None, engine="python", dtype=str, comment="#")

    rs_col = detect_col(df, ["SNP", "RSID", "RS", "MARKERNAME"])
    cpg_col = detect_col(df, ["CPG", "PROBE", "ILMNID", "CG"])
    if not rs_col or not cpg_col:
        raise SystemExit(f"Could not find SNP / CpG columns. Have: {list(df.columns)}")

    def read_manifest(path: str) -> pd.DataFrame:
        with open(path, "r", errors="replace") as f:
            first = f.readline()
        skiprows = 7 if first.strip().startswith("Illumina") else 0
        return pd.read_csv(
            path,
            skiprows=skiprows,
            sep=",",
            dtype=str,
            comment="#",
            low_memory=False,
        )

    man = read_manifest(args.manifest)
    probe_col = detect_col(man, ["NAME", "ILMNID", "PROBEID"])
    gene_col = detect_col(man, ["UCSC_REFGENE_NAME", "REFGENE_NAME", "GENE", "SYMBOL"])
    if not probe_col or not gene_col:
        raise SystemExit(f"Could not find probe / gene columns in manifest. Have: {list(man.columns)}")

    probe_to_genes: dict[str, set[str]] = defaultdict(set)
    for _, row in man.iterrows():
        pid = str(row[probe_col]).strip()
        if not pid or pid == "nan":
            continue
        g = str(row[gene_col]).strip()
        if not g or g == "nan":
            continue
        for token in re_split_genes(g):
            probe_to_genes[pid.upper()].add(token.upper())

    entrez_to_snps: dict[str, set[str]] = defaultdict(set)
    for _, row in df.iterrows():
        rs = str(row[rs_col]).strip()
        cpg = str(row[cpg_col]).strip().upper()
        if not rs.startswith("rs"):
            continue
        genes = probe_to_genes.get(cpg, set())
        for g in genes:
            e = sym_to_e.get(g)
            if e:
                entrez_to_snps[e].add(rs)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as fout:
        for entrez, snps in sorted(entrez_to_snps.items(), key=lambda x: int(x[0])):
            if not snps:
                continue
            line = entrez + " " + " ".join(sorted(snps)) + "\n"
            fout.write(line)

    print(f"Wrote {len(entrez_to_snps)} genes with ≥1 SNP to {out_path}")


def re_split_genes(g: str) -> list[str]:
    g = re.sub(r"\(.*?\)", "", g)
    parts = re.split(r"[;/,|]", g)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        p = p.split()[0]
        if p.endswith("("):
            p = p[:-1]
        if p and p != ".":
            out.append(p)
    return out


if __name__ == "__main__":
    main()
