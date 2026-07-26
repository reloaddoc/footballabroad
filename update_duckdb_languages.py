import duckdb

# 1. Verbindung zur DuckDB-Datenbank herstellen (PFAD HIER ANPASSEN)
db_path = "kickways.duckdb"
con = duckdb.connect(db_path)

# 2. Wörterbuch mit den Übersetzungspaaren
replacements = {
    "Abstiegsrunde": "Relegation Round",
    "Aufstiegsrunde": "Promotion Round",
    "Meisterrunde": "Championship Round",
    "Qualifikationsrunde": "Qualification Round",
}

# 3. Tabellen und Spalten, in denen Liganamen vorkommen
tables_and_columns = [
    ("master_dataset", "from_league"),
    ("master_dataset", "to_league"),
    ("master_dataset", "from_competition"),
    ("master_dataset", "to_competition"),
    ("master_dataset", "from_aggregation"),
    ("master_dataset", "to_aggregation"),
    ("league_dimension", "our_league"),
    ("league_mapping", "our_league"),
]

print("Starte Ersetzung in DuckDB...")

# 4. Updates ausführen
for table, column in tables_and_columns:
    for german, english in replacements.items():
        try:
            con.execute(f"""
                UPDATE {table} 
                SET {column} = REPLACE({column}, '{german}', '{english}')
                WHERE {column} LIKE '%{german}%';
            """)
        except Exception as e:
            # Falls eine Tabelle/Spalte nicht existiert, überspringen
            pass

print("✅ DuckDB erfolgreich auf Englisch aktualisiert!")
con.close()
