import pandas as pd
from pathlib import Path
from goatools.obo_parser import GODag
from goatools.anno.gaf_reader import GafReader
from goatools.goea.go_enrichment_ns import GOEnrichmentStudyNS

ROOT = Path.home() / "fly_rna_1"
GO_REF = ROOT / "go_analysis"
DSEQ_FILES = ROOT / "R_notebooks" / "initial_dseq_analysis"

gobo = GODag(str(GO_REF / 'go-basic.obo'))
gaf = GafReader(str(GO_REF / 'gene_association.fb.fixed'))
gaf_ns = gaf.get_ns2assc()

raw = pd.read_csv(DSEQ_FILES / 'res_starved_vs_fed.csv', index_col=0)
background = set(raw.index[raw['padj'].notna()])
study = set(raw.index[(raw['padj'].notna()) & (raw['padj'] < 0.05)])

go = GOEnrichmentStudyNS(background, gaf_ns, gobo, propagate_counts=True, alpha=0.05, methods=['fdr_bh'])
results = go.run_study(study)
print('diagnostic output')
r = results[0]
print(type(r))
print(type(r.p_fdr_bh))
print(r.p_fdr_bh)
print(r.__dict__)
