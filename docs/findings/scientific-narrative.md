# Scientific narrative

A longer account of the design, the methods choices, and where the analysis currently stands.
The chronology of the project is in the [project history](../labnotes/project-history.md); the
pipeline mechanics and how to reproduce them are in the [README](../../README.md).

## The question

The data come from Li et al. (2024), *Modulation of RNA processing genes during sleep-dependent
memory* (eLife 12:RP89023, https://doi.org/10.7554/eLife.89023; reviewed-preprint title *Sleep and
memory consolidation are linked by RNA processing genes in the Drosophila mushroom body*). The
authors asked what changes transcriptionally in the α′/β′ mushroom-body neurons in the hour after
appetitive training, and whether feeding state after training matters. They labelled the
anterior-posterior α′/β′ neurons with `R35B12-Gal4`, FACS-sorted about 500 GFP+ cells per sample,
and sequenced four replicates each of Trained-Fed, Trained-Starved and Untrained-Fed flies
(NCBI BioProject PRJNA1132369; twelve libraries, SRR29720968–SRR29720979).

This project reanalyses that dataset from the raw reads with an independent pipeline — STAR and
featureCounts rather than the authors' HISAT2 route — to see how far the processed result depends
on the choice of tools. The design has no untrained-starved group, so the comparisons that carry
meaning are training (`UnTrainedFed` vs `TrainedFed`, feeding held constant) and post-training
feeding state (`TrainedFStarved` vs `TrainedFed`, training held constant). The reference throughout
is Ensembl BDGP6.54, release 115.

## Methods, and the choices behind them

Reads are trimmed with fastp, aligned with STAR, and counted with featureCounts; differential
expression is done with DESeq2 and enrichment with goatools. Two points in that chain were decided
from the data rather than by convention.

Strandedness was tested instead of assumed. featureCounts was run under all three `-s` settings and
the assignment rates identified the libraries as unstranded, so `-s 0` is what the counts use;
guessing `-s 1` or `-s 2` here would have roughly halved the counts. Alignment quality was also
confirmed before the counts were trusted: STAR mapped around 85% of reads uniquely with 5–8%
multimapping, and featureCounts assigned 70–75% of reads to features, both consistent with a clean
run against the right reference.

The weak point is downstream. DESeq2 was run interactively in R rather than as a committed script,
so the model and the three contrasts live in a saved `.RData` file and exported CSVs instead of in
versioned code. The count matrix is in the repository, so the statistics can be regenerated, but
the exact model specification has to be reconstructed from the saved session.

## What the differential expression shows

The three contrasts return strikingly different amounts of signal. Counting genes with a non-NA
adjusted p-value below the usual thresholds:

| Contrast | padj < 0.05 | padj < 0.1 | genes tested |
|---|---|---|---|
| `TrainedFStarved` vs `TrainedFed` | 11,894 | 12,044 | 24,253 |
| `UnTrainedFed` vs `TrainedFed` | 182 | 276 | 12,773 |
| `TrainedFStarved` vs `UnTrainedFed` | 70 | 109 | 12,773 |

The first contrast stands apart. Around half of all tested features pass correction, and it has
nearly twice as many testable features as the other two (24,253 against 12,773). A VST ordination
offers a likely reason to look at before interpreting any of this: one sample in the `TrainedFed`
group sits well away from the rest, and within-group clustering is loose. An outlier of that kind
inflates dispersion and can manufacture apparent differential expression, so diagnosing it is the
first order of business.

GO enrichment, run with goatools on the resulting gene lists, returned no significant terms for any
contrast. Against DEG counts in the hundreds to thousands that is surprising, and it points at the
enrichment setup — the significance filter, and the sizes of the study and background sets — rather
than at a biological absence of signal. `study_inv.py` is the diagnostic entry point for that
check.

## Alongside the published result

Li et al. report 59 differentially expressed genes across the two Trained-Fed contrasts (56 down,
3 up in Trained-Fed) at an FDR below 0.1 with a 1.5-fold cutoff, enriched for RNA-processing
functions — ribosome biogenesis, Cajal bodies, RNA polymerase components. They follow up two of
them: *Polr1F*, a regulator of ribosomal RNA transcription whose knockdown increases sleep and
translation but does not affect memory, and *Regnase-1*, whose knockdown reduces both sleep and
long-term memory.

Those 59 genes came from HISAT2 alignments and a different thresholding scheme, so the right way to
read them against the counts above is as a methods comparison still to be done, not a reproduction
or a contradiction. Matching the alignment, the comparison structure and the significance criteria
to the paper's would be the way to find out how much of the difference is biology and how much is
pipeline. The candidate genes the paper settled on — RNA-processing and ribosome-biogenesis factors
— are also a more specific place to start than the classic cAMP/PKA/CREB memory genes an outside
reader might expect this circuit to implicate.

## Limitations

The interactive DESeq2 run is the largest reproducibility gap. The `TrainedFStarved`-vs-`TrainedFed`
contrast cannot be trusted while the `TrainedFed` outlier is unexplained. The empty GO result needs
its filter and background checked before it means anything. A few handoff issues in the scripts are
noted in the README and the project history — chiefly a FASTQ compression mismatch between trimming
and alignment, and a `dropna` call in the results-cleaning step that is never assigned back and so
does nothing.

## Where the biology could go

A single-timepoint bulk experiment can only say so much about a process as fast and as
cell-type-specific as memory consolidation, and the more interesting extensions all push against
that limit. Deconvolving the bulk signal against the Fly Cell Atlas and relating it to the FlyWire
connectome would turn a gene list into statements about particular cell types — Kenyon cells, MBONs
and dopaminergic neurons being the tractable cases. Pairing per-neuron synapse counts with cell-type
metabolic-gene expression would push further, toward a cost-of-computation estimate per cell type.
And a time-course design would address the question a single hour-after-training snapshot cannot:
how the response unfolds over the first few hours. Widmer et al. (2018, GSE115718) — mushroom-body
bulk RNA-seq across four timepoints — is the closest existing dataset to that idea.
