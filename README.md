# Drosophila Brain RNA-seq

Bulk RNA-seq reanalysis of FACS-sorted **α/β′ mushroom body (MB) neurons** of adult
*Drosophila melanogaster*, from NCBI SRA **BioProject PRJNA1132369**. Twelve paired-end
libraries are taken from raw reads through QC, alignment, gene-level quantification,
differential expression, and GO enrichment.

> This repo lives on the Linux compute server at `bg@10.0.0.1:/home/bg/fly_rna_1`. Heavy
> data (~122 GB of FASTQ / BAM / indices) is **not** version-controlled — see
> [Data layout](#data-layout). A Mac-side management/admin workspace mirrors the notes and
> collated history at `~/dev/aaja/drosophila_rna_satellite`.

## Experimental design

The MB is the fly's learning-and-memory centre, so this is a **memory / sleep-memory**
paradigm crossing **training** with **feeding state** — not a plain feeding study. Four
replicates per group, three groups, with **no untrained-starved cell** (the design is
deliberately incomplete):

| Group (DESeq2 label) | Samples | Condition |
|---|---|---|
| `TrainedFStarved` | SRR29720969, 72, 75, 76 | trained, then starved |
| `TrainedFed`      | SRR29720968, 71, 74, 79 | trained, fed |
| `UnTrainedFed`    | SRR29720970, 73, 77, 78 | untrained control, fed |

The two usable axes are **training** (`TrainedFed` vs `UnTrainedFed`, feeding held constant)
and **post-training feeding state** (`TrainedFed` vs `TrainedFStarved`, training held
constant). Any framing as a loose "starved vs fed vs untrained" three-way collapses this
structure — read it against the table above.

The *a priori* candidate set carried into the analysis is the canonical cAMP → PKA → CREB
consolidation machinery: *rutabaga*, *dunce*, *DC0* (PKA-C1), *CrebA/B*, *amnesiac*.

## Reference data

Ensembl **BDGP6.54, release 115** throughout:

| Resource | File |
|---|---|
| Genome (FASTA) | `reference_genome/Drosophila_melanogaster.BDGP6.54.dna.toplevel.fa` |
| Annotation (GTF) | `reference_genome/Drosophila_melanogaster.BDGP6.54.115.gtf` |
| Transcriptome (cDNA) | `reference_transcriptome/Drosophila_melanogaster.BDGP6.54.cdna.all.fa` |
| GO ontology | `go_analysis/go-basic.obo` (Gene Ontology Consortium) |
| GO annotations | `go_analysis/gene_association.fb` (FlyBase FB2026_01) |

## Pipeline

```
SRA retrieval → fastp trim/QC (+ MultiQC) → STAR align → featureCounts
             → DESeq2 (R) → results cleaning → GO enrichment (goatools)
```

| Script | Step | Tool |
|---|---|---|
| `data_retrival.py` | Fetch + convert SRA → FASTQ (Entrez query on PRJNA1132369) | SRA Toolkit / Biopython |
| `trimming.py` | Quality trim, PE, min len 36 / Q20 | fastp (+ MultiQC) |
| `alignment.py` | Build genome index (`--sjdbOverhang 150`, `--genomeSAindexNbases 12`) | STAR |
| `rna_alignment.py` | Align PE reads, coord-sorted BAM | STAR |
| `feature_counts.py` | Gene-level counts, `-p --countReadPairs -s 0` | featureCounts (subread) |
| `expression_changes_cleaning.py` | Post-process DESeq2 results (top 75 by padj) | pandas |
| `go_enrichment.py` | GO enrichment | goatools |
| `study_inv.py`, `go_checker.py`, `pd_check.py`, `go_debug.py` | Enrichment diagnostics | goatools / pandas |
| `salmon_run.py` | Transcript-level quant (**empty — not implemented**) | Salmon (planned) |
| `R_notebooks/initial_dseq_analysis/` | DESeq2 (3 pairwise contrasts, VST PCA) — run **interactively**, saved as `.RData` + CSVs | DESeq2 (R) |

Two methodological choices were made from the data rather than by default:

- **Strandedness was tested, not assumed** — featureCounts under all three `-s` settings
  identified the libraries as **unstranded (`-s 0`)**, avoiding the ~2× undercount `-s 1/2`
  would cause (`strandedness_test_s0.txt[.summary]`).
- **Alignment quality was confirmed before trusting counts** — STAR gave **~85% uniquely
  mapped** (5–8% multimappers), featureCounts assigned ~70–75% of reads.

## Status

| Step | Status |
|---|---|
| SRA retrieval → FASTQ | ✅ Complete (12 samples) |
| fastp trimming + MultiQC | ✅ Complete |
| STAR index + alignment | ✅ Complete (~85% unique) |
| Strandedness check | ✅ Complete → unstranded (`-s 0`) |
| featureCounts (`counts.txt`) | ✅ Complete (~70–75% assigned) |
| DESeq2 (3 contrasts) | ✅ Complete (interactive R; `.RData` + CSVs) |
| Results cleaning (top 75 by padj) | ✅ Complete |
| GO enrichment (goatools) | ⚠️ Run, but significant tables are **empty (header only)** |
| Salmon quantification | ❌ Not implemented (`salmon_run.py` empty; cDNA ref present) |
| Figures (volcano / heatmap / PCA) | ❌ Not generated |
| BAM indexes (`.bai`) | ❌ Not generated |

## Key findings

- **No significant individual-gene changes** survive multiple-testing correction across the
  three contrasts. Obtained with DESeq2 — an independent framework from the original authors'
  — this **reproduces their reported single-gene null**, arguing the absence of signal is a
  property of the data, not of one tool. The empty GO tables are the expected consequence of a
  null DEG input, not a bug (though the significance filter and study-vs-background set sizes
  are worth a sanity pass via `study_inv.py` before calling the null final).
- **The interesting signal is in the variance** — a **strong outlier in the `TrainedFed`
  group** in the VST PCA, with generally loose within-group clustering. This run-to-run
  variance was **not reported in the original paper** and is the prime next object of study:
  if technical it inflates dispersion (a power problem masquerading as a null); if biological
  it is unreported heterogeneity in α/β′ consolidation state. **Diagnose this outlier before
  trusting the DE results.**

## Data layout

Code is tracked; all large data directories are **git-ignored** (`.gitignore`) and live only
on the server:

```
sra_files/  fastq_files/  trimmed_fastq/   # reads (~49G fastq, ~45G trimmed)
genome_index/  reference_genome/  reference_transcriptome/   # refs + STAR index (~2G)
bam_files/                       # STAR alignments (~26G), no .bai yet
feature_counts_output/counts.txt # raw count matrix
cleaned_expression_changes/*_cleaned.csv   # top-75 DEGs per contrast
go_analysis/  go_output/         # GO inputs + (empty) enrichment output
reports/                         # fastp + MultiQC QC reports
R_notebooks/initial_dseq_analysis/deseq2_analysis.RData   # saved DESeq2 session
```

Total ~122 GB on the server; nothing is mirrored to the Mac.

## Documentation

```
README.md                            # this file
PROJECT_SUMMARY.md                   # earlier per-step summary (superseded status table)
docs/labnotes/project-history.md     # full Feb 2026 → present timeline (collated from 4 sources)
docs/findings/scientific-narrative.md # the scientific write-up (findings + future directions)
```

## Environment

- **Python 3.13+, managed with [`uv`](https://docs.astral.sh/uv/)** (`pyproject.toml`).
  Runtime deps: pandas, biopython, goatools, requests, python-dotenv.
  ```bash
  uv sync            # create/refresh .venv and install deps
  uv run <script>.py # run a pipeline step
  ```
- **External tools** (system / conda): fastp, STAR, featureCounts (subread), MultiQC, SRA Toolkit.
- **R**: DESeq2 (the DE step is run interactively in R.app, not via `uv`).

## Known gotchas

- **Renamed project dir.** Older scripts hardcoded `PROJECT_DIR = ~/drosophila_brain_rna_seq_data_1`;
  the live tree is `~/fly_rna_1`. Paths were standardised to `Path(__file__).parent` on
  2026-10-31 — double-check anything older before re-running.
- **Trimmed-FASTQ compression mismatch.** `trimming.py` emits `*_trimmed_1.fastq`
  (uncompressed) while `rna_alignment.py` globs `*1.fastq.gz` and `zcat`s — the handoff only
  works if trimmed files were gzipped out of band.
- **Silent no-op.** `expression_changes_cleaning.py` calls `dropna(subset=['padj'])` without
  assigning the result back, so NA-padj rows aren't dropped (the sort just hides them).
- **GO annotation needed repair.** goatools' `GafReader` rejected FlyBase's raw
  `gene_association.fb`; enrichment runs against a hand-repaired `gene_association.fb.fixed`.
- **DESeq2 is not scripted.** The model + contrasts live in a saved `.RData` and exported CSVs,
  not in versioned code — the single biggest reproducibility liability.

## Next steps

1. Diagnose the `TrainedFed` PCA outlier / loose clustering before trusting the DE results —
   it is both the suspected power problem and the most promising novel lead.
2. Sanity-check / loosen the GO significance filter; confirm study vs background set sizes
   (`study_inv.py`).
3. Generate the missing figures (volcano, heatmap, PCA export).
4. Implement or formally drop `salmon_run.py` (transcript-level quant).
5. Longer-horizon: map cell-type markers in the expression changes onto the FlyWire connectome
   / Fly Cell Atlas (see `docs/findings/scientific-narrative.md` §5).

## See also

- `PROJECT_SUMMARY.md` — earlier per-step summary (note: predates the GO run and uses the loose
  group labels; this README supersedes its status table).
- `docs/labnotes/project-history.md` — full Feb 2026 → present timeline, collated from four
  sources.
- `docs/findings/scientific-narrative.md` — the scientific write-up (findings + future
  directions).

These two docs were collated on the Mac-side admin workspace
(`~/dev/aaja/drosophila_rna_satellite`), which keeps mirror copies.
