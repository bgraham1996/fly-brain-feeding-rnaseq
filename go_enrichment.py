import pandas as pd
from pathlib import Path
from goatools.obo_parser import GODag
from goatools.anno.gaf_reader import GafReader
from goatools.goea.go_enrichment_ns import GOEnrichmentStudyNS


experiments = ['starved_vs_fed', 'starved_vs_untrained', 'untrained_vs_fed']

""""files"""
SERVER = Path.home()
ROOT = SERVER / "fly_rna_1"
DSEQ_FILES = ROOT / "R_notebooks" / "initial_dseq_analysis"
OUT = ROOT / "go_output"
GO_REF = ROOT / "go_analysis"

OUT.mkdir(exist_ok=True)

gobo = GODag(str(GO_REF / 'go-basic.obo'))
gaf = GafReader(str(GO_REF / 'gene_association.fb.fixed'))
gaf_ns = gaf.get_ns2assc()

remove_te = True

def results_to_df(results):
    """Convert goatools result records to a dataframe."""
    records = [
        {
            'GO': r.GO,
            'name': r.name,
            'NS': r.NS,
            'enrichment': r.enrichment,
            'p_uncorrected': r.p_uncorrected,
            'p_fdr_bh': r.p_fdr_bh,
            'study_count': r.study_count,
            'study_n': r.study_n,
            'pop_count': r.pop_count,
            'pop_n': r.pop_n,
            'study_items': ','.join(r.study_items) if r.study_items else '',
        }
        for r in results
    ]
    df = pd.DataFrame(records)
    df['fold_enrichment'] = (df['study_count'] / df['study_n']) / (df['pop_count'] / df['pop_n'])
    return df


for experiment in experiments:
    file_name = f'res_{experiment}.csv'
    print(f"\nEnriching for {experiment}")
    raw = pd.read_csv(DSEQ_FILES / file_name, index_col=0)
    
    # Add to script before the filter
    print(f"Before TE filter: {len(raw)} rows")
    if remove_te:
        raw = raw[raw.index.str.startswith('FBgn')]
        print(f"After TE filter: {len(raw)} rows")

    if remove_te is True:
        raw = raw[raw.index.str.startswith('FBgn')]

    background = set(raw.index[raw['padj'].notna()])
    study = set(raw.index[(raw['padj'].notna()) & (raw['padj'] < 0.05)])

    print(f"Background size: {len(background)}")
    print(f"Study size: {len(study)}")

    go = GOEnrichmentStudyNS(background, gaf_ns, gobo, propagate_counts=True, alpha=0.05, methods=['fdr_bh'])
    results = go.run_study(study)

    df = results_to_df(results)
    sig = df[(df['p_fdr_bh'] < 0.05) & (df['enrichment'] == 'e') & (df['study_count'] >= 3) & (df['fold_enrichment'] >= 2)].sort_values('p_fdr_bh')

    if remove_te is True:
        mod = '_no_te'
    else:
        mod = ''

    df.to_csv(OUT / f'{experiment}_go_raw{mod}.csv', index=False)
    sig.to_csv(OUT / f'{experiment}_go_significant{mod}.csv', index=False)

    print(f"Total terms tested: {len(df)}")
    print(f"Significant enriched terms (FDR < 0.05): {len(sig)}")
