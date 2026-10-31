import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
data = pd.read_csv(PROJECT_DIR / 'R_notebooks' / 'initial_dseq_analysis' / 'res_starved_vs_fed.csv')

print(data.head(10))
