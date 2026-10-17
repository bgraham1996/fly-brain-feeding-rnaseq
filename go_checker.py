import pandas as pd

dir = 'go_output/'
file = 'starved_vs_untrained_go_significant_no_te.csv'
path = dir + file

data = pd.read_csv(path)

print(data.head(10))


