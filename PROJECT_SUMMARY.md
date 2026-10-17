# Drosophila Brain RNA-seq Project Summary

**Date:** 2026-04-25  
**Project directory:** `~/drosophila_brain_rna_seq_data_1`

---

## Overview

Bulk RNA-seq analysis of *Drosophila melanogaster* brain tissue comparing three experimental conditions:
- **Starved**
- **Fed**
- **Untrained** (naive/unstimulated control)

12 paired-end samples (SRR29720968–SRR29720979) sourced from NCBI SRA.

---

## Reference Data

| Resource | File | Source |
|---|---|---|
| Genome (FASTA) | `reference_genome/Drosophila_melanogaster.BDGP6.54.dna.toplevel.fa` | Ensembl release 115 |
| Annotation (GTF) | `reference_genome/Drosophila_melanogaster.BDGP6.54.115.gtf` | Ensembl release 115 |
| Transcriptome | `reference_transcriptome/Drosophila_melanogaster.BDGP6.54.cdna.all.fa` | Ensembl |
| GO ontology | `go_analysis/go-basic.obo` | Gene Ontology Consortium |
| GO annotations | `go_analysis/gene_association.fb` | FlyBase FB2026_01 (Feb 2026) |

---

## Pipeline Steps Completed

### 1. Quality Trimming (`trimming.py`)
- **Tool:** fastp
- **Parameters:** min length 36 bp, min quality Q20, paired-end
- **Output:** `trimmed_fastq/SRR*_trimmed_{1,2}.fastq.gz` (12 samples)
- **QC Reports:** `reports/trimming/html/` (per-sample), `reports/trimming/json/` (per-sample)
- **MultiQC Report:** `reports/trimming/multiqc/multiqc_report.html`

### 2. Genome Index Generation (`alignment.py`)
- **Tool:** STAR
- **Parameters:** `--sjdbOverhang 150`, `--genomeSAindexNbases 12`, 4 threads
- **Output:** `genome_index/` (SA, SAindex, chrName.txt, geneInfo.tab, etc.)

### 3. Read Alignment (`rna_alignment.py`)
- **Tool:** STAR
- **Parameters:** paired-end, BAM sorted by coordinate, 8 threads, `zcat` for gzipped input
- **Output:** `bam_files/SRR*_Aligned.sortedByCoord.out.bam` (12 BAM files)
- **Typical alignment rate:** ~85% uniquely mapped (e.g. SRR29720968: 85.44%, SRR29720975: 85.67%)
- **Multi-mapping:** ~5–8% per sample

### 4. Strandedness Test
- **File:** `strandedness_test_s0.txt` / `strandedness_test_s0.txt.summary`
- **Result:** Library confirmed as **unstranded** (`-s 0`)

### 5. Feature Counting (`feature_counts.py`)
- **Tool:** featureCounts (subread)
- **Parameters:** `-p --countReadPairs` (paired-end), `-s 0` (unstranded), 4 threads
- **GTF:** BDGP6.54.115
- **Output:** `feature_counts_output/counts.txt`
- **Assignment rates (selected samples):**
  - SRR29720968: 13.75M assigned, 4.27M multi-mapping, 1.69M no feature
  - SRR29720975: 28.21M assigned, 10.0M multi-mapping, 3.07M no feature
  - SRR29720979: 29.97M assigned, 8.97M multi-mapping, 2.99M no feature

### 6. Differential Expression (`R_notebooks/initial_dseq_analysis/`)
- **Tool:** DESeq2 (R)
- **Comparisons run (3 pairwise):**
  - `res_starved_vs_fed.csv`
  - `res_starved_vs_untrained.csv`
  - `res_untrained_vs_fed.csv`
- **Output columns:** baseMean, log2FoldChange, lfcSE, stat, pvalue, padj
- **R workspace saved:** `deseq2_analysis.RData`

### 7. Results Cleaning (`expression_changes_cleaning.py`)
- Drops rows with NA padj, sorts by padj ascending, retains top 75 hits per comparison
- **Output:** `cleaned_expression_changes/`
  - `starved_vs_fed_cleaned.csv`
  - `starved_vs_untrained_cleaned.csv`
  - `untrained_vs_fed_cleaned.csv`

**Top DEGs — Starved vs Fed (top 5 by padj):**

| Gene ID | baseMean | log2FC | padj |
|---|---|---|---|
| FBgn0050467 | 250.7 | +6.37 | 2.23e-11 |
| FBgn0000552 | 58.5 | +19.83 | 9.82e-08 |
| FBgn0002872 | 154.3 | +5.98 | 3.13e-07 |
| FBgn0038769 | 97.0 | +6.03 | 4.24e-07 |
| FBti0020244 | 56.2 | -5.38 | 1.39e-05 |

---

## Current State

| Step | Status |
|---|---|
| Raw data download | Complete |
| Quality trimming (fastp) | Complete |
| Genome index (STAR) | Complete |
| Read alignment (STAR) | Complete |
| Strandedness check | Complete |
| Feature counting (featureCounts) | Complete |
| DESeq2 differential expression | Complete |
| Results cleaning (top 75 by padj) | Complete |
| GO analysis | **Not started** (data files downloaded) |
| Salmon quantification | **Not started** (`salmon_run.py` is empty) |

---

## Pending / Next Steps

1. **GO enrichment analysis** — FlyBase annotation (`gene_association.fb`) and GO ontology (`go-basic.obo`) are downloaded; analysis script not yet written. Likely candidate tools: `goatools` (Python) or `clusterProfiler` (R).
2. **Salmon quantification** — `salmon_run.py` exists but is empty. Could provide transcript-level quantification as an alternative/complement to the STAR→featureCounts approach.
3. **Visualizations** — No volcano plots, heatmaps, or PCA plots have been generated yet.
4. **BAM indexing** — BAI index files are not present; needed for genome browsers and some downstream tools.

---

## Key Files

```
trimming.py                      # fastp trimming script
alignment.py                     # STAR genome index build
rna_alignment.py                 # STAR read alignment
feature_counts.py                # featureCounts quantification
expression_changes_cleaning.py   # DESeq2 results post-processing
salmon_run.py                    # (empty — not started)
test.py                          # scratch/diagnostic script

R_notebooks/initial_dseq_analysis/deseq2_analysis.RData   # saved R session
feature_counts_output/counts.txt                           # raw count matrix
cleaned_expression_changes/*_cleaned.csv                   # top 75 DEGs per comparison
go_analysis/gene_association.fb                            # FlyBase GO annotations
go_analysis/go-basic.obo                                   # GO term hierarchy
```

---

## Environment

- Python 3.13+, managed with `uv` (`pyproject.toml`)
- Python dependencies: pandas, biopython, requests, python-dotenv, pathlib
- External tools: fastp, STAR, featureCounts (subread), multiqc
- R packages: DESeq2
