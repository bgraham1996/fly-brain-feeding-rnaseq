import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DSEQ_DIR = PROJECT_DIR / 'R_notebooks' / 'initial_dseq_analysis'
GO_OUT = PROJECT_DIR / 'go_output'

for exp in ['starved_vs_fed', 'starved_vs_untrained', 'untrained_vs_fed']:
    raw = pd.read_csv(DSEQ_DIR / f'res_{exp}.csv', index_col=0)
    bg = raw['padj'].notna().sum()
    study = ((raw['padj'].notna()) & (raw['padj'] < 0.05)).sum()
    print(f"{exp}: background={bg}, study={study}")


df = pd.read_csv(GO_OUT / 'starved_vs_fed_go_raw.csv')

# Top 20 by uncorrected p-value, enriched only, with reasonable counts
top = df[(df['enrichment'] == 'e') & (df['study_count'] >= 3)].sort_values('p_uncorrected').head(5)
print(top[['GO', 'name', 'NS', 'p_uncorrected', 'p_fdr_bh', 'study_count', 'pop_count', 'fold_enrichment']].to_string())

df = pd.read_csv(GO_OUT / 'starved_vs_fed_go_raw.csv')
print(df.groupby('NS')['p_fdr_bh'].describe())
print(df['p_fdr_bh'].value_counts().head())
