# Reanalysis of α/β′ Mushroom Body RNA-seq — A Scientific Narrative

*A working account of the project for a reader already familiar with it: what we set out to
do, the problems we hit, how we resolved them, and what we found. Written as a scientific
narrative rather than an admin log — the project-management digest lives in
[`project-history.md`](../labnotes/project-history.md), alongside the code/data in this repo.
Collated on the Mac-side admin workspace (`~/dev/aaja/drosophila_rna_satellite`), which keeps
a mirror copy.*

---

## 1. Premise and design

The project is an independent reanalysis of the bulk RNA-seq from **BioProject PRJNA1132369** —
FACS-sorted **α/β′ mushroom body (MB) neurons** of adult *Drosophila melanogaster*, collected under
a memory/sleep paradigm that crosses **training** with **feeding state**. Twelve paired-end
libraries (SRR29720968–SRR29720979), four per group, across three groups:

| Group | Samples | |
|---|---|---|
| **TrainedFStarved** | SRR29720969, 72, 75, 76 | trained, then starved |
| **TrainedFed**      | SRR29720968, 71, 74, 79 | trained, fed |
| **UnTrainedFed**    | SRR29720970, 73, 77, 78 | untrained control, fed |

Note the design is deliberately **incomplete** — there is no untrained-starved cell — so the two
usable axes are *training* (TrainedFed vs UnTrainedFed, feeding held constant) and *post-training
feeding state* (TrainedFed vs TrainedFStarved, training held constant). Any statement framed loosely
as "starved vs fed vs untrained" collapses this structure and should be read against the table above.

The scientific question is the one the α/β′ compartment is built for: does a learning episode, and
the metabolic state in which it is consolidated, leave a transcriptional signature in these Kenyon
cells — and is that signature better described at the single-gene level or at the level of the
canonical **cAMP → PKA → CREB** consolidation machinery? The *a priori* candidate set we carried
into the analysis was *rutabaga*, *dunce*, *DC0* (PKA-C1), *CrebA/B*, and *amnesiac*.

Reference throughout: **Ensembl BDGP6.54, release 115** (top-level genome, matched GTF, and cDNA
for the planned transcript-level route).

---

## 2. The pipeline, and why each choice was made

Reads → `fastp` trim/QC (+ MultiQC) → **STAR** genome alignment → `featureCounts` gene-level
quantification → **DESeq2** → GO enrichment (goatools). A Salmon transcript-level arm was scoped as
a parallel check but never implemented.

Two methodological decisions are worth recording because they were made from the data, not by
default:

- **Strandedness was tested, not assumed.** featureCounts was run under all three
  `-s` settings; assignment rates identified the libraries as **unstranded (`-s 0`)**. This is the
  correct call for the kit used and prevents the ~2× undercount that `-s 1/2` would have produced.
- **Alignment quality was confirmed before trusting counts.** STAR gave **~85% uniquely mapped**
  with 5–8% multimappers — healthy for fly brain — and featureCounts assigned ~70–75% of reads to
  features, consistent with real intronic/intergenic signal rather than a reference mismatch.

DESeq2 was run **interactively in R.app** (VST for the ordination, three pairwise Wald contrasts),
rather than as a committed script. This is the single biggest reproducibility liability in the
project: the model and contrasts live in a saved `.RData` + exported CSVs, not in versioned code.

---

## 3. Problems worked through

### 3.1 Infrastructure was the first real experiment

The retrieval phase ran on the Mac and hit a wall that had nothing to do with biology:

- **macOS Gatekeeper killed the SRA Toolkit.** `prefetch`/`fasterq-dump` were SIGKILLed on launch
  because the downloaded binaries carried the quarantine xattr. Fix: `xattr -dr
  com.apple.quarantine` on the toolkit.
- **`fasterq-dump` blew the disk budget.** Its scratch-space model raised "disk-limit exceeded" on a
  ~228 GB drive with ~15 GB free. We abandoned the prefetch→dump path for a streaming
  `fastq-dump --split-files --gzip`, which brought the footprint down enough to convert **one** of
  the twelve samples (SRR29720975, 39.6 M pairs, ~5.8 GB) before storage became the hard limit.

The conclusion drawn — correctly — was that the Mac was the wrong machine. A repurposed gaming PC
became an Ubuntu compute server (`benslabs`), on a direct ethernet link (`10.0.0.1` ↔ Mac
`10.0.0.2`) with Wake-on-LAN and an SSHFS mount, ~474 GB NVMe. **Every quantitative result in the
project comes from this box.** The Mac-side Feb–Mar phase is now only of historical interest.

### 3.2 Reference and annotation friction

- **Project-directory rename.** Early scripts hardcode
  `PROJECT_DIR = ~/drosophila_brain_rna_seq_data_1`; the live tree is `~/fly_rna_1`. Paths were later
  standardised to `Path(__file__).parent`, but anything older than that commit will look in the
  wrong place.
- **GO annotation had to be repaired.** goatools' `GafReader` rejected FlyBase's raw
  `gene_association.fb`; the enrichment runs against a hand-repaired `gene_association.fb.fixed`.
  Worth knowing before anyone re-runs enrichment against a fresh annotation drop.

### 3.3 Latent handoff bugs (flagged, not all fixed)

These do not invalidate the headline result but will bite a re-run:

- **Trimmed-FASTQ compression mismatch.** `trimming.py` emits `*_trimmed_1.fastq` (uncompressed)
  while `rna_alignment.py` globs `*1.fastq.gz` and `zcat`s — the step only connects if the trimmed
  files were gzipped out of band.
- **A silent no-op in results cleaning.** `expression_changes_cleaning.py` calls
  `dropna(subset=['padj'])` without assigning the result back, so NA-padj rows are not actually
  dropped; the subsequent sort merely hides them.
- **No BAM indexes.** `.bai` files were never generated, so IGV and index-dependent downstream tools
  can't be pointed at the alignments yet.

---

## 4. Findings

### 4.1 The single-gene result reproduces the original paper

Across the three DESeq2 contrasts, **no genes survive multiple-testing correction** — there are no
significant individual-gene expression changes. Critically, this was obtained with **DESeq2**, a
different differential-expression framework from the original authors', and it **agrees with their
reported null** at the single-gene level. Reproducing a null with an independent method is a real,
if undramatic, result: it argues the absence of signal is a property of the data, not of one tool's
shrinkage or dispersion model.

The GO enrichment is consistent with this: it was run, and its **significant tables are empty
(header-only)**. That is the expected consequence of having no significant DEG input, not a bug —
though the significance filtering and the study-vs-background set sizes are still worth a sanity
pass (`study_inv.py` is the diagnostic) before the null is called final.

### 4.2 The more interesting signal is in the variance

The novel observation — and the thing the original paper did **not** report — is **run-to-run
variance** visible in the VST PCA: a **strong outlier in the TrainedFed group** against generally
loose within-group clustering. Mechanistically this is ambiguous until resolved: it could be a
genuine biological state difference in one trained-fed animal, a FACS/library artefact, or a batch
effect. Either way it is the correct next object of study, because:

1. If technical, it inflates within-group dispersion and is part of *why* nothing reaches
   significance — i.e. it is a power problem masquerading as a biological null.
2. If biological, unreported heterogeneity in the consolidation state of α/β′ neurons is itself a
   finding worth characterising.

So the current scientific position is: **no single-gene effect (confirmed, independently),
pathway-level signal too weak to call, and an unexplained variance structure that has to be
diagnosed before either of the first two can be trusted.**

---

## 5. Where the biology goes next

The project has consistently pointed past the single-timepoint bulk null toward designs that match
the α/β′ circuit's actual resolution and dynamics:

- **Two-scale GO.** Population-level enrichment to surface themes (e.g. kinase activity), then
  gene-level annotation on specific DEGs read against the fly memory literature to propose a
  concrete module (calcium influx → CaMKII → CREB). Caveat we flagged: don't hang a mechanistic
  story on IEA-only annotations.
- **Connectome + cell-atlas integration.** Bridge the bulk signal to the **FlyWire** connectome
  (~8,453 cell types) and the **Fly Cell Atlas** scRNA-seq (~250 brain cell types) through shared
  marker genes — Kenyon cells, MBONs and DANs being the tractable anchors — and test for cell-type
  *proportion* shifts by deconvolution (CIBERSORT / MuSiC / DWLS). The resolution mismatch (FlyWire
  finer than scRNA-seq) is the limiting factor.
- **Metabolic cost of computation.** The genuinely new angle the connectome unlocks: per-neuron
  synapse counts as an energetic-cost proxy, cross-referenced with cell-type OXPHOS/glycolysis/
  mito-biogenesis expression, to estimate cost-of-computation per cell type — building on Davie et
  al. 2018's SCENIC regulatory-heterogeneity work.
- **Time-course pivot.** The stated biological interest is early post-intervention dynamics
  (1h/2h/3h), which a single-timepoint bulk design cannot see. Closest public datasets: **Widmer et
  al. 2018** (GSE115718; MB bulk, paired/unpaired courtship conditioning, 4 timepoints × 4 reps — the
  best match), **Yan et al. 2025** (courtship LTM time course + CREB-engram scRNA-seq), **Crocker et
  al. 2016** (MB cell-type RNA-seq by memory state), plus circadian (**Abruzzi 2017** GSE77451,
  **Ma 2021**) and developmental (**Kurmangaliyev 2020**, **Xie 2021** GSE161228) sets. Caveat: dense
  1–3h sampling is rare in memory paradigms, and cross-dataset annotation drift can swamp the
  biological signal.

---

## 6. Honest status line

Retrieval → trimming → alignment → counting → DESeq2 → GO have all **run end to end**. The result is
a **well-supported null at the gene and pathway level that corroborates the original study**, plus
**one unexplained variance structure (the TrainedFed PCA outlier)** that is simultaneously the prime
suspect for the weak power and the most promising lead for a novel finding. Figures (volcano,
heatmap, PCA export) are not yet generated; the Salmon transcript-level arm is unimplemented. The
immediate scientific priority is diagnosing that outlier — everything downstream depends on whether
the null is a biological fact or a dispersion artefact.
