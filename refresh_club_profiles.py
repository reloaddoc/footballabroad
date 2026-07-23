import pandas as pd
from database import write_table

df = pd.read_csv(
    "output/club_profiles.csv",
    encoding="utf-8-sig"
)

write_table("club_profiles", df)

print(f"Imported {len(df):,} club profiles into DuckDB.")
