#!/usr/bin/env Rscript
# Usage: Rscript 08_fdr_genes.R results/GGE/magma_default.genes.out [FDR]
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  quit(status = 1, save = "no")
}
f <- args[[1]]
q <- if (length(args) >= 2) as.numeric(args[[2]]) else 0.05
t <- read.table(f, header = TRUE, sep = "", quote = "", comment.char = "")
if (!"P" %in% names(t)) {
  stop("Column P not found in ", f)
}
t$FDR <- p.adjust(t$P, method = "fdr")
sig <- t[t$FDR <= q, ]
out <- sub("\\.genes\\.out$", paste0(".genes.fdr", gsub("^0\\.", "", as.character(q)), ".tsv"), f)
write.table(sig, file = out, sep = "\t", row.names = FALSE, quote = FALSE)
message("Wrote ", nrow(sig), " FDR<=", q, " genes to ", out)
