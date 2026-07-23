import pandas as pd
from database import write_table

TABLES = {
    "transfers": "output/transfers.csv",
    "clubs": "output/clubs.csv",
    "club_profiles": "output/club_profiles.csv",
    "player_profiles": "output/player_profiles.csv",
    "career_paths": "output/career_paths.csv",
}


def build():

    for table, file in TABLES.items():
        df = pd.read_csv(file, encoding="utf-8-sig")
        write_table(table, df)
        print(f"✓ Imported {table} ({len(df):,} rows)")


if __name__ == "__main__":
    build()
