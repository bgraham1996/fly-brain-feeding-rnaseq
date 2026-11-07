# Project history

A chronological account of how this reanalysis was built, from the first data download to its
current state. The pipeline itself and the scientific write-up live in the
[README](../../README.md) and [scientific narrative](../findings/scientific-narrative.md); this
document is the log of what happened and when.

The dataset is from Li et al. (2024), *Modulation of RNA processing genes during sleep-dependent
memory* (eLife 12:RP89023, https://doi.org/10.7554/eLife.89023), deposited as NCBI BioProject
PRJNA1132369 — twelve paired-end RNA-seq libraries of FACS-sorted α′/β′ mushroom-body neurons
across Trained-Fed, Trained-Starved and Untrained-Fed conditions.

## The data labels

One thing to keep straight throughout. The project's older summaries describe the three groups
loosely as starved / fed / untrained, but the labels actually used in the DESeq2 metadata encode
the training-by-feeding design:

| Label used here | Samples | Paper's condition |
|---|---|---|
| `TrainedFStarved` | SRR29720969, 72, 75, 76 | Trained-Starved |
| `TrainedFed` | SRR29720968, 71, 74, 79 | Trained-Fed |
| `UnTrainedFed` | SRR29720970, 73, 77, 78 | Untrained-Fed |

There is no untrained-starved group, so the two informative axes are training (`UnTrainedFed` vs
`TrainedFed`) and post-training feeding state (`TrainedFStarved` vs `TrainedFed`).

## Timeline

| When | What happened |
|---|---|
| Feb 2026 | Retrieval began on the Mac: a Biopython/Entrez query against PRJNA1132369, then the SRA Toolkit. Two problems surfaced immediately — macOS Gatekeeper killed the toolkit binaries until the quarantine attribute was cleared, and `fasterq-dump` ran out of scratch space on a nearly full disk. Streaming `fastq-dump --split-files --gzip` got one sample (SRR29720975) down before storage ran out. |
| Feb 22 2026 | The storage limit forced the real decision: a spare PC was turned into an Ubuntu compute server (`benslabs`) on a direct ethernet link to the Mac, with ~474 GB of NVMe. Every quantitative result since comes from this machine. |
| Feb–Mar 2026 | On the server: all twelve samples downloaded, trimmed with fastp and summarised with MultiQC, aligned with STAR (~85% uniquely mapped), checked for strandedness (unstranded, `-s 0`), and counted with featureCounts into `counts.txt`. |
| Mar 10–11 2026 | DESeq2 run interactively in R: three pairwise contrasts exported, VST ordination for QC. |
| Mar 24 2026 | First commit to the server git repo. |
| Apr 2026 | Extension ideas captured — identifying cell-type markers in the expression changes and mapping them onto a connectome. |
| Oct 2026 | GO enrichment added with goatools, plus the first project documentation and result tables. |
| Oct 30–31 2026 | Repository cleanup: stop tracking bytecode, add the SRA retrieval step to version control, anchor script paths on `Path(__file__).parent`. |
| Nov 2026 | Documentation pass: source paper cited, findings corrected against the actual DESeq2 output, derived data removed from the repository (count matrix kept), README and these docs rewritten. |

## Where it stands

Retrieval, trimming, alignment, counting, DESeq2 and GO enrichment have all run end to end. The
differential-expression results are summarised in the README and discussed in the scientific
narrative; in short, the three contrasts return very different amounts of signal (from 70 up to
~12,000 genes past correction), one of them behaves anomalously, and GO enrichment returned
nothing significant — a result that needs its filter and background set checked rather than taken
at face value.

Still outstanding: the Salmon transcript-level arm was scoped but never written; no figures
(volcano, heatmap, PCA export) have been generated; and the BAMs have no `.bai` indexes.

## Things that tripped it up

The infrastructure was the first real obstacle — the Mac could not hold the data, and most of
February went into building the server rather than analysing anything. After that the friction was
smaller but worth recording. An early project directory (`~/drosophila_brain_rna_seq_data_1`) was
renamed to `~/fly_rna_1`, and scripts predating the switch to `Path(__file__).parent` still point
at the old name. The trimming and alignment steps disagree on compression — `trimming.py` writes
uncompressed FASTQ while `rna_alignment.py` expects gzip — so they only connect if the trimmed
files were gzipped in between. goatools rejected FlyBase's raw GO annotation, so enrichment runs
against a hand-repaired copy. And the DESeq2 statistics were run interactively rather than scripted,
which is the main reason the analysis is not yet a clean one-command rerun.

## Directions considered

Beyond finishing the core pipeline, a few larger directions were sketched out:

- **Cell-type deconvolution and the connectome.** Bridge the bulk signal to the FlyWire connectome
  and the Fly Cell Atlas single-cell data through shared marker genes — Kenyon cells, MBONs and
  dopaminergic neurons being the tractable anchors — and test for shifts in cell-type proportion
  across conditions. The resolution mismatch between the two atlases is the limiting factor.
- **Metabolic cost.** Using per-neuron synapse counts as an energetic-cost proxy, cross-referenced
  with cell-type expression of metabolic genes, to estimate a cost of computation per cell type.
- **A time-course design.** The biological interest is in early post-training dynamics, which a
  single-timepoint bulk experiment cannot see. Widmer et al. (2018, GSE115718) is the closest
  public dataset — mushroom-body bulk RNA-seq across four timepoints — with Crocker et al. (2016)
  and several circadian and developmental sets as further options.

## How this was reconstructed

The timeline above was pieced together from the server git history, the project's own summary
files, and local working notes. Where the older notes and the live results disagreed — most
importantly on whether the reanalysis found significant differential expression — the live DESeq2
output was treated as the source of truth and the notes corrected to match.
