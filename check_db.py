import duckdb
con = duckdb.connect(r"data/kickways.duckdb")
tables = con.sql("SHOW TABLES").fetchall()
print([t[0] for t in tables])

print("\n--- league_dimension columns ---")
cols = con.sql("DESCRIBE league_dimension").fetchall()
for c in cols:
    print(c)

print("\n--- sample league_dimension ---")
sample = con.sql("SELECT league, country, league_group FROM league_dimension WHERE league_group IS NOT NULL AND league_group != '' LIMIT 10").fetchall()
for row in sample:
    print(row)

print("\n--- total with league_group ---")
count = con.sql("SELECT COUNT(*) FROM league_dimension WHERE league_group IS NOT NULL AND league_group != ''").fetchone()
print(count[0])

con.close()
