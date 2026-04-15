#!/usr/bin/env python3
"""
Normalize ILAE / EPIGAD GWAS summary files for MAGMA --pval.

MAGMA v1.10 expects three tab-separated fields: SNP, P, per-SNP sample size N
(use ncol=3). ILAE files provide Effective_N; otherwise ILAE_DEFAULT_N is repeated.
"""
from __future__ import annotations

import argparse
import gzip
import os
import sys
from pathlib import Path

import pandas as pd


def open_maybe_gzip(path: str):
    path = str(path)
    if path.endswith(".gz"):
        return gzip.open(path, "rt", errors="replace")
    return open(path, "r", errors="replace")


def sniff_columns(path: str, nrows: int = 5000) -> pd.DataFrame:
    """Read a sample of rows with flexible separator."""
    for sep in ["\t", ",", " ", r"\s+"]:
        try:
            df = pd.read_csv(
                open_maybe_gzip(path),
                sep=sep,
                dtype=str,
                nrows=nrows,
                comment="#",
                engine="python" if sep == r"\s+" else "c",
            )
            if len(df.columns) >= 3:
                df.columns = [str(c).strip() for c in df.columns]
                return df
        except Exception:
            continue
    df = pd.read_csv(open_maybe_gzip(path), dtype=str, nrows=nrows, comment="#")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def pick_snp_col(cols: list[str]) -> str | None:
    up = {c: c.upper() for c in cols}
    for key in (
        "SNP",
        "MARKERNAME",
        "RSID",
        "ID",
        "VARIANT_ID",
    ):
        for c in cols:
            if c.upper() == key:
                return c
    return None


def pick_p_col(cols: list[str]) -> str | None:
    for c in cols:
        u = c.upper().replace(" ", "_")
        if u in ("P", "PVALUE", "P_VALUE", "PVAL", "P-VALUE"):
            return c
        if "P_BOLT" in u and "LMM" in u:
            return c
    return None


def pick_n_col(cols: list[str]) -> str | None:
    for c in cols:
        u = c.upper().replace(" ", "_")
        if u in ("N", "WEIGHT", "SAMPLESIZE", "SAMPLE_SIZE", "N_SAMPLES", "EFFECTIVE_N"):
            return c
    return None


def discover(sumstats_dir: Path) -> None:
    patterns = ("*.gz", "*.txt", "*.tsv", "*.csv", "*.meta", "*.META")
    hits: list[Path] = []
    for pat in patterns:
        hits.extend(sumstats_dir.rglob(pat))
    hits = sorted({p.resolve() for p in hits if p.is_file()})
    print(f"# {len(hits)} candidate files under {sumstats_dir}\n")
    for p in hits[:200]:
        try:
            rel = p.relative_to(sumstats_dir)
        except ValueError:
            rel = p
        print(rel)
    if len(hits) > 200:
        print(f"... ({len(hits) - 200} more)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Prepare GWAS summary stats for MAGMA")
    ap.add_argument("--discover", action="store_true", help="List candidate files under ILAE_SUMSTATS_DIR")
    ap.add_argument("--input", type=str, help="Input summary statistics file")
    ap.add_argument("--out-dir", type=str, required=False, default="prepared")
    ap.add_argument("--label", type=str, default="GGE", help="Output basename label")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    sumstats_dir = Path(os.environ.get("ILAE_SUMSTATS_DIR", root / "data" / "ilae3_sumstats"))

    if args.discover:
        if not sumstats_dir.is_dir():
            print(f"Missing directory: {sumstats_dir}", file=sys.stderr)
            sys.exit(1)
        discover(sumstats_dir)
        return

    if not args.input:
        ap.error("Provide --input or use --discover")
    in_path = Path(args.input)
    if not in_path.is_file():
        print(f"Not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.label}_magma.pval"

    sample = sniff_columns(str(in_path))
    cols = list(sample.columns)
    snp_c = pick_snp_col(cols)
    p_c = pick_p_col(cols)
    n_c = pick_n_col(cols)
    if not snp_c or not p_c:
        print("Could not detect SNP / P columns. Columns seen:", cols, file=sys.stderr)
        sys.exit(1)

    default_n = float(os.environ.get("ILAE_DEFAULT_N", "82500"))
    if n_c:
        print(f"Using columns: SNP={snp_c}, P={p_c}, N={n_c} (per variant)")
    else:
        print(f"Using columns: SNP={snp_c}, P={p_c}, N={default_n:g} (constant ILAE_DEFAULT_N)")

    df_iter = pd.read_csv(
        open_maybe_gzip(str(in_path)),
        sep=None,
        engine="python",
        dtype=str,
        chunksize=200_000,
        comment="#",
    )

    n_written = 0
    with open(out_path, "w") as fout:
        for chunk in df_iter:
            chunk.columns = [str(c).strip() for c in chunk.columns]
            if snp_c not in chunk.columns or p_c not in chunk.columns:
                continue
            snp = chunk[snp_c].astype(str)
            p = pd.to_numeric(chunk[p_c], errors="coerce")
            if n_c and n_c in chunk.columns:
                nvals = pd.to_numeric(chunk[n_c], errors="coerce")
            else:
                nvals = pd.Series(default_n, index=chunk.index, dtype="float64")
            m = snp.notna() & p.notna() & (p > 0) & (p <= 1) & nvals.notna() & (nvals >= 1.0)
            sub = chunk.loc[m, [snp_c]].copy()
            sub["_P"] = p[m]
            sub["_N"] = nvals[m]
            sub[snp_c] = sub[snp_c].str.strip()
            sub = sub[~sub[snp_c].str.fullmatch("", na=False)]
            for _, row in sub.iterrows():
                fout.write(f"{row[snp_c]}\t{row['_P']:.6E}\t{row['_N']:.8g}\n")
                n_written += 1

    print(f"Wrote {n_written} variants (3 columns: SNP P N) to {out_path}")
    meta = out_path.with_suffix(".pval.meta.txt")
    meta.write_text(
        f"input={in_path}\nlabel={args.label}\nsnp_col={snp_c}\np_col={p_c}\n"
        f"n_col={n_c or f'constant:{default_n}'}\nmagma_pval_ncol=3\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
