from pathlib import Path
import duckdb

DB = "data/kickways.duckdb"

Path("data").mkdir(exist_ok=True)

con = duckdb.connect(DB)

print("Database created.")

con.close()
