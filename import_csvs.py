from pathlib import Path
import duckdb

DB = "data/kickways.duckdb"
OUTPUT = Path("output")

con = duckdb.connect(DB)

files = [
    "transfers",
    "players",
    "clubs",
    "club_profiles",
    "player_profiles",
    "career_paths",
    "league_dimension",
    "league_mapping",
    "opta_rankings",
]

for table in files:

    csv = OUTPUT / f"{table}.csv"

    if not csv.exists():
        print(f"Skipping {table}")
        continue

    print(f"Importing {table}...")

    con.execute(f"""
        CREATE OR REPLACE TABLE {table} AS
        SELECT *
        FROM read_csv_auto('{csv.as_posix()}',
                           HEADER=TRUE);
    """)

print()
print("Finished.")

con.close()
