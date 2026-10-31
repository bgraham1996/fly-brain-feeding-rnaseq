import pandas as pd
from pathlib import Path

# paths anchored to this script's directory (the repo, where the data lives)
PROJECT_DIR = Path(__file__).resolve().parent
IN_DIR = PROJECT_DIR / 'R_notebooks' / 'initial_dseq_analysis'
CLEANED_DIR = PROJECT_DIR / 'cleaned_expression_changes'
CLEANED_DIR.mkdir(parents=True, exist_ok=True)

csv_files = sorted(IN_DIR.glob("*.csv"))
csv_files = [f for f in csv_files if not f.name.startswith('._')]

for file in csv_files:
    file_name = file.name
    file_name = file_name.replace('res_', '')
    file_name = file_name.replace('.csv', '')
    data = pd.read_csv(file, encoding='latin-1')
    data.dropna(subset=['padj'])
    data = data.sort_values(by='padj', ascending=True)
    data = data.head(75)

    data.to_csv(CLEANED_DIR / (file_name + '_cleaned.csv'))





