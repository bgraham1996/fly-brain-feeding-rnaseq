import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
path = PROJECT_DIR / 'go_output' / 'starved_vs_untrained_go_significant_no_te.csv'

data = pd.read_csv(path)

print(data.head(10))


