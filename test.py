import pandas as pd

df = pd.read_csv("output/master_dataset.csv", encoding="utf-8-sig")

leagues = sorted(
    pd.concat([
        df["from_league"],
        df["to_league"]
    ])
    .dropna()
    .unique()
)

for league in leagues:
    print(league)
