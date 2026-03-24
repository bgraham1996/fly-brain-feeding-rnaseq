import pandas as pd


data = pd.read_csv('R_notebooks/initial_dseq_analysis/res_starved_vs_untrained.csv')

print(data['padj'].dtype)


