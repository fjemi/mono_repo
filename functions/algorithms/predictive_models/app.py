
# import numpy

import pandas

file_path = '/home/olufemij/Downloads/train.csv'
df = pandas.read_csv(file_path, index_col='PassengerId')

# lowercase column names
mapper = {}
for column in df.columns:
  mapper[column] = column.lower()
df.columns = list(mapper.values())


# determine uniqueness
uniqueness = {}
for column in df.columns:
  print(df[column].value_counts())
  # values = df[column].unique()
  # store = {}
  # for value in values:
  #   store[value] = df[column].count(value) / len(df[column])
  # uniqueness[column] = sum(list(store.values()))


  # uniqueness[column] = len(df[column].unique()) / len(df[column])
  # uniqueness[column] = round(uniqueness[column] * 100, 2)
print(uniqueness)