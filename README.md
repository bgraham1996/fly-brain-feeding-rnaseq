# Drosophila mushroom-body RNA-seq

An independent reanalysis, from raw reads, of the bulk RNA-seq in Li et al. (2024). The
dataset profiles α′/β′ mushroom-body neurons of *Drosophila melanogaster* under a sleep /
memory-consolidation paradigm; this repository rebuilds the quantification and differential
expression with a STAR → featureCounts → DESeq2 pipeline rather than the authors' HISAT2 route,
and takes it through GO enrichment.

**Source dataset.** Li Y, Chouhan NS, Zhang SL, Moore RS, Noya SB, Shon J, Yue Z, Sehgal A
(2024), *Modulation of RNA processing genes during sleep-dependent memory*, eLife 12:RP89023,
https://doi.org/10.7554/eLife.89023 (reviewed-preprint title: *Sleep and memory consolidation
are linked by RNA processing genes in the Drosophila mushroom body*). Reads come from NCBI
BioProject **PRJNA1132369** — 12 paired-end libraries, SRR29720968–SRR29720979.

The code lives on a Linux compute server at `bg@10.0.0.1:/home/bg/fly_rna_1`; the ~122 GB of
reads, alignments and indices stay there and are not tracked (see [Repository layout](#repository-layout)).

## The experiment

Li et al. labelled the anterior-posterior α′/β′ mushroom-body neurons with `R35B12-Gal4`,
dissociated and FACS-sorted ~500 GFP+ cells per sample, and sequenced them one hour after
appetitive training. The mushroom body is the fly's learning-and-memory centre, so the design
crosses training with feeding state to separate sleep-dependent from training-dependent change.
Four replicates sit in each of three conditions:

| Condition (label used here) | Samples | In the paper |
|---|---|---|
| `TrainedFStarved` | SRR29720969, 72, 75, 76 | Trained-Starved — controls for sleep-dependent change |
| `TrainedFed` | SRR29720968, 71, 74, 79 | Trained-Fed |
| `UnTrainedFed` | SRR29720970, 73, 77, 78 | Untrained-Fed — controls for training-dependent change |

There is no untrained-starved group, so the comparisons that mean something are training
(`UnTrainedFed` vs `TrainedFed`) and post-training feeding state (`TrainedFStarved` vs
`TrainedFed`); a flat "starved vs fed vs untrained" reading loses that. Everything downstream uses
Ensembl **BDGP6.54, release 115** — genome, matching GTF, and the cDNA set for the (unbuilt)
transcript-level route.

## Pipeline

Reads are trimmed with fastp (paired-end, min length 36, Q20) and summarised with MultiQC,
aligned to the genome with STAR, and counted per gene with featureCounts against the BDGP6.54.115
annotation. Strandedness was not assumed: featureCounts was run under all three `-s` settings and
the assignment rates identify the libraries as unstranded (`-s 0`), which is what the counts use.
STAR maps ~85% of reads uniquely (5–8% multimapping) and featureCounts assigns ~70–75%, so the
count matrix rests on healthy alignments. Differential expression is done in R with DESeq2 across
three pairwise contrasts, with a VST ordination for QC; GO enrichment runs on the resulting gene
lists with goatools.

| Script | Does |
|---|---|
| `data_retrival.py` | Entrez query on PRJNA1132369, SRA fetch, FASTQ conversion |
| `trimming.py` | fastp trim + QC, MultiQC summary |
| `alignment.py` | STAR genome index (`--sjdbOverhang 150`, `--genomeSAindexNbases 12`) |
| `rna_alignment.py` | STAR paired-end alignment, coordinate-sorted BAM |
| `feature_counts.py` | featureCounts gene-level quantification (`-p --countReadPairs -s 0`) |
| `expression_changes_cleaning.py` | trims the DESeq2 tables to the top 75 by padj |
| `go_enrichment.py` | GO enrichment; `study_inv.py`, `go_checker.py`, `pd_check.py`, `go_debug.py` are its diagnostics |
| `R_notebooks/initial_dseq_analysis/` | the DESeq2 session (three contrasts + VST PCA), saved as `.RData` and CSVs |
| `salmon_run.py` | placeholder for a transcript-level arm; never written |

The DESeq2 step was run interactively in R.app rather than as a committed script, so the model
and contrasts live in the saved `.RData` and the exported CSVs, not in versioned code. That is the
main thing standing between this repository and a one-command rerun of the statistics.

## Reproducing the quantification

The one data file kept in the repository is the gene-level count matrix,
`feature_counts_output/counts.txt`. Everything from DESeq2 onward can be regenerated from it
without touching the raw reads: load it into R and rerun the contrasts in
`R_notebooks/initial_dseq_analysis/`. The Python side is managed with
[`uv`](https://docs.astral.sh/uv/) (Python 3.13):

```bash
uv sync             # create .venv and install deps (pandas, biopython, goatools, …)
uv run go_enrichment.py
```

STAR, featureCounts (subread), fastp, MultiQC and the SRA Toolkit are external tools expected on
`PATH`; DESeq2 runs in R, outside the uv environment.

## Results

Differential expression returns very different amounts of signal across the three contrasts
(counts below are genes with a non-NA `padj` under the stated cutoff):

| Contrast | padj < 0.05 | padj < 0.1 | genes tested |
|---|---|---|---|
| `TrainedFStarved` vs `TrainedFed` | 11,894 | 12,044 | 24,253 |
| `UnTrainedFed` vs `TrainedFed` | 182 | 276 | 12,773 |
| `TrainedFStarved` vs `UnTrainedFed` | 70 | 109 | 12,773 |

The first contrast is an outlier in its own right: about half of all tested features pass
correction, and it carries nearly twice as many testable features as the other two (24k vs 13k).
A VST PCA shows one strong outlier in the `TrainedFed` group and loose within-group clustering,
which is the obvious thing to resolve before reading too much into those numbers. GO enrichment
(goatools) returned no significant terms for any contrast; given the DEG counts above, the study
and background set sizes and the significance filter need checking before that is taken at face
value (`study_inv.py` is the entry point).

For comparison, Li et al. report 59 differentially expressed genes (56 down, 3 up in Trained-Fed)
across the two Trained-Fed contrasts at FDR < 0.1 with a 1.5-fold cut, enriched for RNA-processing
functions, and follow up *Polr1F* (a regulator of rRNA transcription) and *Regnase-1*. They used
HISAT2 and a different thresholding scheme, so the gap between their 59 and the counts here is a
methods comparison still to be made, not a like-for-like result.

## Repository layout

Only the count matrix is tracked. The large directories below are git-ignored and exist only on
the server:

```
sra_files/  fastq_files/  trimmed_fastq/          reads (~49G raw, ~45G trimmed)
genome_index/  reference_genome/  reference_transcriptome/   refs + STAR index (~2G)
bam_files/                                          STAR alignments (~26G); no .bai indexes
feature_counts_output/counts.txt                    the gene × sample count matrix (tracked)
cleaned_expression_changes/                         top-75 DEG tables per contrast
go_analysis/  go_output/                            GO inputs and (empty) enrichment output
reports/                                            fastp + MultiQC reports
R_notebooks/initial_dseq_analysis/deseq2_analysis.RData   saved DESeq2 session
```

## Caveats

A few things are worth knowing before rerunning any of this. The DESeq2 statistics are not
scripted (above), which is the largest reproducibility gap. `trimming.py` writes uncompressed
`*_trimmed_1.fastq` while `rna_alignment.py` expects `*1.fastq.gz` and `zcat`s it, so the two only
connect if the trimmed files were gzipped between steps. In `expression_changes_cleaning.py` the
`dropna(subset=['padj'])` call is never assigned back, so NA-padj rows are not actually dropped —
the sort just hides them. GO enrichment runs against a hand-repaired `gene_association.fb.fixed`
because goatools' `GafReader` rejects FlyBase's raw annotation. The BAMs have no `.bai` indexes
yet. And some early scripts hardcode an older project path (`~/drosophila_brain_rna_seq_data_1`);
paths were later anchored on `Path(__file__).parent`, but anything predating that should be
checked before it is run.

## More detail

- [`docs/labnotes/project-history.md`](docs/labnotes/project-history.md) — how the project was
  built, start to present.
- [`docs/findings/scientific-narrative.md`](docs/findings/scientific-narrative.md) — the
  longer write-up of design, methods and where the analysis stands.
