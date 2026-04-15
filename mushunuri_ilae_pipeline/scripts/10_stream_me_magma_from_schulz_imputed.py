#!/usr/bin/env python3
"""
Stream Schulz et al. *imputed* cis-meQTL table (NatCommun_Schulz2017_ImputedSNPs_meQTLs.txt)
from a local .zip or plain .txt, map CpG → gene via Illumina 450k manifest, and write MAGMA
`--gene-annot` lines: ENTREZ rsID1 rsID2 ...

The imputed file is ~29 GB uncompressed; this script reads line-by-line (stdin or unzip -p).

Example:
  unzip -p data/raw/schulz2017/NatCommun_Schulz2017_ImputedSNPs_meQTLs.zip \\
    | python3 scripts/10_stream_me_magma_from_schulz_imputed.py \\
        --manifest data/raw/GPL13534_...csv \\
        --gene-info tools/magma/ref/Homo_sapiens.gene_info.gz \\
        --max-p 1e-4 \\
        --out tools/magma/annot/me_magma.genes.annot
"""
from __future__ import annotations

import argparse
import gzip
import re
import sys
import zipfile
from collections import defaultdict

import pandas as pd


def load_gene_info(path: str) -> dict[str, str]:
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


def read_manifest(path: str) -> dict[str, set[str]]:
    with open(path, "r", errors="replace") as f:
        first = f.readline()
    skiprows = 7 if first.strip().startswith("Illumina") else 0
    man = pd.read_csv(path, skiprows=skiprows, sep=",", dtype=str, low_memory=False)
    name_col = None
    gene_col = None
    for c in man.columns:
        u = str(c).upper().replace(" ", "_")
        if u in ("NAME", "ILMNID"):
            name_col = c
        if u in ("UCSC_REFGENE_NAME", "REFGENE_NAME", "UCSC_REF_GENE_NAME"):
            gene_col = c
    if not name_col or not gene_col:
        raise SystemExit(f"Manifest missing Name/UCSC_RefGene_Name columns: {list(man.columns)[:30]}")

    probe_to_genes: dict[str, set[str]] = defaultdict(set)
    for _, row in man.iterrows():
        pid = str(row[name_col]).strip().upper()
        if not pid or pid == "NAN":
            continue
        g = str(row[gene_col]).strip()
        if not g or g == "nan":
            continue
        for token in split_gene_field(g):
            probe_to_genes[pid].add(token.upper())
    return probe_to_genes


def split_gene_field(g: str) -> list[str]:
    g = re.sub(r"\(.*?\)", "", g)
    out = []
    for p in re.split(r"[;/,|]", g):
        p = p.strip()
        if not p:
            continue
        p = p.split()[0]
        if p.endswith("("):
            p = p[:-1]
        if p and p != ".":
            out.append(p)
    return out


def open_meqtl_source(path: str):
    if path.endswith(".zip"):
        z = zipfile.ZipFile(path)
        names = z.namelist()
        inner = next((n for n in names if n.endswith(".txt")), names[0])
        return z.open(inner, "r")
    return open(path, "rb")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--meqtl-zip", help="Path to NatCommun_Schulz2017_ImputedSNPs_meQTLs.zip")
    ap.add_argument("--meqtl-txt", help="Path to decompressed .txt (optional)")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--gene-info", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-p", type=float, default=1e-4, help="Keep rows with p-value <= this (default 1e-4)")
    args = ap.parse_args()

    if not args.meqtl_zip and not args.meqtl_txt:
        ap.error("Provide --meqtl-zip or --meqtl-txt")

    sym_to_e = load_gene_info(args.gene_info)
    probe_to_genes = read_manifest(args.manifest)

    source = open_meqtl_source(args.meqtl_txt or args.meqtl_zip)
    entrez_snps: dict[str, set[str]] = defaultdict(set)
    n_in = 0
    n_kept = 0

    # Binary stream → text
    import io

    text = io.TextIOWrapper(source, encoding="utf-8", errors="replace")
    header = text.readline().rstrip("\n").split("\t")
    if header[0].upper() != "SNP":
        raise SystemExit(f"Unexpected header: {header}")
    # SNP  gene  beta  t-stat  p-value  — second column is CpG id
    for line in text:
        n_in += 1
        if n_in % 5_000_000 == 0:
            print(f"... processed {n_in/1e6:.1f}M lines, kept {n_kept/1e6:.2f}M", file=sys.stderr)
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 5:
            continue
        snp, cpg, _b, _t, p_s = parts[0], parts[1], parts[2], parts[3], parts[4]
        if not snp.startswith("rs"):
            continue
        try:
            p = float(p_s)
        except ValueError:
            continue
        if p > args.max_p:
            continue
        cpg = cpg.strip().upper()
        if not cpg.startswith("CG"):
            continue
        n_kept += 1
        genes = probe_to_genes.get(cpg, ())
        for g in genes:
            e = sym_to_e.get(g)
            if e:
                entrez_snps[e].add(snp)

    text.detach()
    source.close()

    out_path = args.out
    with open(out_path, "w") as fout:
        for entrez in sorted(entrez_snps, key=int):
            snps = entrez_snps[entrez]
            if not snps:
                continue
            fout.write(entrez + " " + " ".join(sorted(snps)) + "\n")

    print(
        f"Lines scanned: {n_in}, kept (p<={args.max_p}): {n_kept}, genes with SNPs: {len(entrez_snps)}",
        file=sys.stderr,
    )
    print(out_path)


if __name__ == "__main__":
    main()
