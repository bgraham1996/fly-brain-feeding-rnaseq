# Drosophila Brain RNA-seq — Collated Project History

> Collated 2026-11-06 from four scattered sources (see **Sources** below). A management/admin
> digest, collated on the Mac-side admin workspace (`~/dev/aaja/drosophila_rna_satellite`,
> which keeps a mirror copy) and now kept in the project repo alongside the code. Where sources
> disagree, the discrepancy is flagged rather than silently resolved.

## What the project is

Bulk RNA-seq analysis of *Drosophila melanogaster* **brain** tissue, reanalysing a public
dataset: NCBI SRA **BioProject PRJNA1132369**, **12 paired-end samples**
(SRR29720968–SRR29720979), four per group across **three groups**. The pipeline runs raw
reads → quality trimming → STAR alignment → gene-level counting → DESeq2 differential
expression → GO enrichment, with Salmon transcript quantification planned but never written.

**Group labels — an important discrepancy.** The project's own summary files describe the
three conditions loosely as **Starved / Fed / Untrained**. The actual labels in the DESeq2
metadata are **`TrainedFStarved` / `TrainedFed` / `UnTrainedFed`** — a training-crossed-with-
feeding design, with *no* untrained-and-starved group. Sample→group assignment (read from the
R session):

| Group | Samples |
|---|---|
| TrainedFStarved | SRR29720969, 72, 75, 76 |
| TrainedFed | SRR29720968, 71, 74, 79 |
| UnTrainedFed | SRR29720970, 73, 77, 78 |

Reference throughout: **Ensembl BDGP6.54, release 115** (top-level genome FASTA, matching GTF,
and cDNA transcriptome).

## Biological context

(Drawn from the claude.ai "Bioinformatics and computational biology" project discussions — see
Sources #4. This context is *not* written down in the repo or vault and is the main thing the
browser pass added.)

The dataset is **bulk RNA-seq of α/β′ mushroom body (MB) neurons** — the dataset the original
authors produced by driving a Gal4 line in MB neurons and FACS-sorting them. The mushroom body is
the fly's learning-and-memory centre, so the Trained/Untrained × Fed/Starved design is a
**memory / sleep-memory** paradigm, not a simple feeding study. The relevant, exhaustively
characterised biology is the **cAMP / PKA / CREB** memory-consolidation pathway; candidate genes
worth grepping the DEG lists for include *rutabaga*, *dunce*, *DC0* (PKA catalytic subunit),
*CrebA/B*, and *amnesiac*. (Genes mentioned as possible α/β′ hits in discussion: *Polr1F*,
*Regnase-1* — treat as examples to verify, not confirmed results.)

This framing also explains the headline result below: the original paper reported **no
significant individual-gene changes**, and the reanalysis reproduces that — so the interesting
signal is at the population/pathway level and in the unreported run-to-run variance, not in
single genes.

## Timeline

| When | Milestone | Source |
|---|---|---|
| **2026-02-17/18** | Data-retrieval phase begins on the **Mac**. Biopython-Entrez query against PRJNA1132369 → `prefetch` → FASTQ conversion. Hit two blockers: macOS Gatekeeper SIGKILL-ing SRA Toolkit (fixed with `xattr -dr com.apple.quarantine`), and `fasterq-dump` "disk-limit exceeded" on a ~228 GB drive with ~15 GB free. Resolved by switching to streaming `fastq-dump --split-files --gzip`. Only **1 of 12** samples (SRR29720975, 39.6M read pairs, ~5.8 GB) converted — storage became the bottleneck. | Vault: *2026-02-18 … progress*; archived repo |
| **2026-02-18** | Recognised ~70 GB needed for the full set; decided external SSD + a dedicated machine were required. | Vault: *External data storage and the terminal* |
| **2026-02-22** | **Server stood up.** Repurposed gaming PC → Ubuntu server `benslabs`, dual-network (WiFi for internet + direct ethernet `10.0.0.1` ↔ Mac `10.0.0.2`), Wake-on-LAN, SSHFS mount at `~/server`, and zsh aliases (`server-wake/ssh/mount/unmount`). ~474 GB NVMe. This is the compute box all later work runs on. | Vault: *Server set up Summary* |
| **2026-02–03** | On the server (via the `~/server` SSHFS mount): downloaded all 12 samples, fastp trimming + MultiQC, STAR index build + alignment (~85% unique), strandedness test → unstranded (`-s 0`), featureCounts → `counts.txt`. | Archived repo; server repo; vault |
| **2026-03-10/11** | **DESeq2** run interactively in R.app (not scripted): three pairwise contrasts exported; VST PCA run. Decided to "clean up and make a git repo". | Vault: *Dseq … analysis*, *PCA and Variance* |
| **2026-03-24** | First git commit on the server repo — `2dfff5d "initial dump"`. | Server git log |
| **2026-04-28** | Project-extension ideas captured: identify cell-type markers in the expression changes; map those cell types onto a connectome. | Vault: *Drosophila Brain RNA Seq* |
| **2026-10-17** | `6f6a52d` — **GO enrichment pipeline** (goatools), project docs (`PROJECT_SUMMARY.md`, `CLAUDE_DESKTOP_CONTEXT.md`), and result tables added. | Server git log |
| **2026-10-24** | Detailed file-by-file **pipeline walkthrough** written up in the Obsidian vault (LLM-authored). | Vault: *… Pipeline Walkthrough* |
| **2026-10-30/31** | `fc9f210`, `343c3b4`, `bed323b`, `b5beb7d`, `c48b92a` — untrack local-only context file; add SRA retrieval script for direct server execution; standardise all script paths to `Path(__file__).parent`; stop tracking `__pycache__`. | Server git log |
| **2026-11-06** | This admin workspace created on the Mac; history collated. Server repo: `main`, **7 commits, clean**, ~122 GB data. | This session |

## Current state & key findings

Every step from retrieval through featureCounts, DESeq2, and GO enrichment has been run end to
end. Status per step:

| Step | Status |
|---|---|
| SRA retrieval → FASTQ | Complete (12 samples on server) |
| fastp trimming + MultiQC | Complete |
| STAR index + alignment | Complete (~85% unique, 5–8% multimap) |
| Strandedness check | Complete → unstranded (`-s 0`) |
| featureCounts (`counts.txt`) | Complete (~70–75% assigned) |
| DESeq2 (3 contrasts) | Complete (interactive R; `.RData` + CSVs saved) |
| Results cleaning (top 75 by padj) | Complete |
| GO enrichment (goatools) | **Run, but all significant tables are empty (header only)** |
| Salmon quantification (`salmon_run.py`) | **Not implemented** (empty file; cDNA ref present) |
| Figures (volcano/heatmap/PCA) | Not generated |

**The headline scientific result (from the Claude Desktop project discussion):** the pipeline's
finding of **no significant individual-gene expression changes** *agrees with the original
authors' finding*, despite using a different differential-expression tool (DESeq2). The novel
contribution surfaced so far is the **variance in one sequencing run that the original paper did
not report** — this corresponds to the **strong outlier in the `TrainedFed` group** seen in the
VST PCA, alongside generally loose clustering. The empty GO result therefore reads as a genuinely
weak biological signal, not a code fault.

> Note: this contradicts the older `PROJECT_SUMMARY.md` on the server, which still lists GO as
> "not started". GO *has* been run; it simply returned nothing significant.

## Research directions & extensions discussed

Beyond finishing the core pipeline, the Claude Desktop project worked through several ways to
extend the project into something more novel. Captured here because none of it is in the repo:

- **GO at two scales.** Population-level enrichment ("kinase activity is over-represented") to
  spot themes, then gene-level GO annotation on the specific DEGs — combined with fly memory
  literature — to sketch a candidate regulatory module (e.g. calcium influx → CaMKII → CREB).
  Caveat flagged: watch IEA evidence codes when anchoring a mechanistic story on one gene.
- **Connectome + cell-atlas integration** (the fleshed-out version of the vault's "map cell
  types onto a connectome" idea). Bridge the bulk DE signal to the **FlyWire** connectome
  (~8,453 cell types) and the **Fly Cell Atlas** scRNA-seq (~250 brain cell types) via shared
  cell-type marker genes. MB Kenyon cells, MBONs and DANs are the tractable cases; resolution
  mismatch (FlyWire finer than scRNA-seq) is the main limit. Deconvolution (CIBERSORT / MuSiC /
  dwls) to test cell-type-proportion shifts across conditions. Tooling: `navis`/`natverse`,
  `coconatfly`, `fafbseg`, `scanpy`/`anndata`.
- **Metabolic-cost angle** (flagged as the genuinely novel contribution the connectome enables):
  per-neuron synapse counts as a proxy for energetic cost, cross-referenced with cell-type
  metabolic-gene expression (OXPHOS/glycolysis/mito-biogenesis) → cell-type-resolved
  cost-of-computation estimates. Builds on Davie 2018's SCENIC regulatory-heterogeneity findings.
- **Time-course pivot** (user's stated interest: expression changes at 1h/2h/3h post-intervention).
  Candidate public datasets surfaced: **Widmer et al. 2018** (GSE115718, MB bulk, paired/unpaired
  courtship conditioning, 4 timepoints × 4 reps — "close to ideal"); **Yan et al. 2025** (Nat
  Commun, courtship LTM time course + CREB-engram scRNA-seq); **Crocker et al. 2016** (MB
  cell-type RNA-seq by memory state); circadian sets **Abruzzi 2017** (GSE77451) and **Ma 2021**
  (eLife) with the 2024 FlyWire clock connectome; developmental sets **Kurmangaliyev 2020**,
  **Xie 2021** (GSE161228). Caveat: dense 1h/2h/3h sampling is rare in memory paradigms (mostly
  2–4 timepoints); cross-dataset annotation drift can dominate biological signal.
- **Dissemination / portfolio plan.** Write the project up as a narrative via **Obsidian
  Publish** (already the user's note system), with interactive figures deployed as **Streamlit**
  apps embedded by iframe, static PNG/SVG fallbacks for hero figures, and a possible **bioRxiv**
  short report if a genuinely novel result (e.g. the metabolic-cost analysis) lands.

## Open threads / next steps

1. Investigate the `TrainedFed` PCA outlier and loose clustering before trusting the DE results —
   this is also the candidate novel finding (unreported run variance).
2. Sanity-check / loosen the GO significance filter; confirm study vs background set sizes
   (`study_inv.py` is the diagnostic entry point).
3. Generate the still-absent figures (volcano, heatmap, PCA).
4. Implement or formally drop `salmon_run.py` (transcript-level quant as an alternative route).
5. Longer-horizon idea: identify cell-type markers in the expression changes and map them onto a
   *Drosophila* brain connectome.

## Known gotchas (carried across sources)

- **Renamed project dir.** Older scripts hardcode `PROJECT_DIR = ~/drosophila_brain_rna_seq_data_1`;
  newer GO scripts use `~/fly_rna_1` (the dir that exists). The 2026-10-31 commits standardised
  paths to `Path(__file__).parent`, but double-check before re-running anything old.
- **Trimmed-FASTQ compression mismatch** — `trimming.py` writes `*_trimmed_1.fastq` (no `.gz`) but
  `rna_alignment.py` globs `*1.fastq.gz` + `zcat`; the handoff only works if trimmed files were
  gzipped out of band.
- **Silent no-op** — the `dropna(subset=['padj'])` in `expression_changes_cleaning.py` isn't
  assigned back, so it does nothing (the sort masks it).
- **GO annotation needed repair** — goatools' `GafReader` rejected the raw `gene_association.fb`;
  the pipeline uses a repaired `gene_association.fb.fixed`.
- **No BAM indexes** (`.bai`) — needed for IGV and some downstream tools.
- **Retrieval script not in early repo** — the SRA retrieval step was only added to the server
  git repo on 2026-10-31; earlier it lived outside version control.

## Sources

| # | Source | Location | What it holds |
|---|---|---|---|
| 1 | **Server repo** (live) | `bg@10.0.0.1:/home/bg/fly_rna_1` — own remote `github.com/bgraham1996/fly-brain-feeding-rnaseq`, main, 7 commits | The actual code, data (~122 GB), `PROJECT_SUMMARY.md`, `CLAUDE_DESKTOP_CONTEXT.md`, R session + results |
| 2 | **Archived early version** | `~/Inbox/archive-dev-projects/Developer/drosophila_brain_rna_seq` (NOT `~/dev/archive/`) | The Feb–Mar 2026 Mac-side phase: `data_retrival.py`, `trimming.py`, `reference_download.py`, `multiqc_report.html`, `runinfo.csv`. Git-inited but **0 commits** — history is in file timestamps |
| 3 | **Obsidian vault (Immrama)** | `~/Vaults/Immrama/Immrama/Note Processing/` | Dated log + write-ups: `New Notes/Drosophila Brain RNA Seq.md` (chronological log), `… /2026-02-18 … progress.md`, `… /Dseq Differential Analysis ….md`, `… /PCA and Variance.md`, `… /Server set up Summary.md`, `… /External data storage and the terminal.md`, `Trees/Drosophila Brain RNA-seq - Pipeline Walkthrough.md`, and the `Trees/Gene Ontology - *` cluster (GO reference) |
| 4 | **Claude Desktop / claude.ai project** | claude.ai Project **"Bioinformatics and computational biology"** (`/project/019c3280-c5b5-74ce-aa55-78cfa7d8a926`) | The project's primary working journal — ~30 conversations Feb–Jun 2026 covering retrieval, QC, alignment, DESeq2, GO, the server setup, git cleanup, and the research-direction/extension brainstorming. Read via browser 2026-11-06. The biological context and extension directions above come from here. |

### Note on the Claude Desktop source

The earlier guess of a project named "drosophila rna-seq" was a conversation title in a fragmented
local IndexedDB cache; the **authoritative** source is the claude.ai project **"Bioinformatics and
computational biology"**, read directly in the browser on 2026-11-06. Its conversation list below
doubles as a day-by-day index of the project's history. A few later conversations in it are
tangents to *other* bio projects (cell-simulation → `genetic-sims`; DNA/protein LMs → `protein-llm`;
intron/gene-size → the gene-length project) and are marked accordingly.

#### Conversation index (newest → oldest; ★ = directly this repo)

| Date | Conversation | |
|---|---|---|
| Jun 29 | Intron and gene size expansion in nervous system evolution | (gene-length project) |
| Jun 10 | Language models for DNA and proteins | (protein-llm) |
| Jun 1 | Object-oriented cell simulation design | (genetic-sims) |
| Apr 29 | Statistical foundations for bioinformatics | ★ |
| Apr 29 | Understanding pathwayPCA tool | ★ |
| Apr 29 | Python GO enrichment analysis setup | ★ |
| Apr 26 | Expanding transcription data beyond single timepoint | ★ (extensions) |
| Apr 25 | Resuming drosophila project work | ★ (GO-at-two-scales, LLM-for-lit-mining) |
| Apr 24 | Remote server access and wake-on-LAN setup | ★ |
| Mar 24 | Unstaging files before gitignore | ★ (git cleanup) |
| Mar 19 | Bioinformatics research scientist career fit | (career; personal) |
| Mar 11 | GO enrichment analysis from DESeq2 comparisons | ★ |
| Mar 10 | Understanding PCA in bioinformatics analysis | ★ |
| Mar 10 | BAM files alignment complete | ★ |
| Mar 7 | Trimming completion and multiqc report review | ★ |
| Mar 4 | Trimming script review and fastq file status | ★ |
| Mar 4 | RNA-seq quality control analysis review | ★ |
| Mar 2 | Batch quality control for fastq files | ★ |
| Feb 27 | RNA analysis directions and network approaches | ★ (directions + portfolio plan) |
| Feb 26 | Hiding mounted mcfuse volume from desktop | ★ |
| Feb 22 | Server setup and project continuity | ★ |
| Feb 21 | Ubuntu server development tools setup | ★ |
| Feb 20 | Understanding RNA-seq QA reports | ★ |
| Feb 20 | QA workflow for sequence data | ★ |
| Feb 19 | Setting up a Windows PC as a local bioinformatics server | ★ |
| Feb 18 | RNA-seq data retrieval from NCBI using SRA tools | ★ |
| Feb 18 | We've spoken previously about … | (ambiguous) |
| Feb 17 | Programmatic access to RNA-seq data from BioProject | ★ |
| Feb 17 | Managing Python environments with conda and uv | ★ |
| Feb 17 | Terminal-based tools for bioinformatics notebooks | ★ |

Only the direction-setting conversations were read in full (Feb 27, Apr 25, Apr 26); the rest are
indexed by title/date — their procedural content (QC, trimming, alignment, DESeq2 mechanics) is
already captured from the server repo and the vault. Open any by title in the project if more
detail is needed.
