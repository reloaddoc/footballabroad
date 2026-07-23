from database import read_table

df = read_table("master_dataset")

print(df.head())

print(len(df))
