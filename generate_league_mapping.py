from pathlib import Path

import pandas as pd

# =====================================================
# Dateien
# =====================================================

INPUT = "output/league_dimension.csv"

OUTPUT = "output/league_mapping.xlsx"

# =====================================================
# Laden
# =====================================================

df = pd.read_csv(
    INPUT,
    encoding="utf-8-sig",
)

print()
print("=" * 70)
print("GENERATE LEAGUE MAPPING")
print("=" * 70)
print()

print(f"{len(df):,} Ligen geladen.")

# =====================================================
# Nur fehlende League Groups
# =====================================================

mapping = df.copy()

mapping = mapping[
    mapping["league_group"]
    .fillna("")
    .eq("")
]

print(
    f"{len(mapping):,} Ligen ohne League Group gefunden."
)
# =====================================================
# Spalten auswählen
# =====================================================

columns = [

    "country",

    "competition_code",

    "league",

    "league_group",

    "level",

    "category",

    "is_professional",

    "notes",

]

mapping = mapping[columns]

# =====================================================
# Sortieren
# =====================================================

mapping = (

    mapping

    .sort_values(

        [

            "country",

            "league",

        ]

    )

    .reset_index(

        drop=True

    )

)

# =====================================================
# Excel-Datei schreiben
# =====================================================

with pd.ExcelWriter(

    OUTPUT,

    engine="openpyxl",

) as writer:

    mapping.to_excel(

        writer,

        sheet_name="League Mapping",

        index=False,

    )

    ws = writer.sheets["League Mapping"]

    # Spaltenbreiten
    widths = {

        "A": 20,

        "B": 18,

        "C": 45,

        "D": 40,

        "E": 10,

        "F": 15,

        "G": 18,

        "H": 40,

    }

    for col, width in widths.items():

        ws.column_dimensions[col].width = width
        # =====================================================
# Vorschau
# =====================================================

print()

print("=" * 70)
print("VORSCHAU")
print("=" * 70)

print()

if len(mapping):

    print(

        mapping.head(20)

    )

else:

    print(

        "Keine fehlenden League Groups gefunden."

    )

# =====================================================
# Statistik
# =====================================================

print()

print("=" * 70)
print("STATISTIK")
print("=" * 70)

print(f"Gesamte Ligen          : {len(df):,}")

print(f"Fehlende League Groups : {len(mapping):,}")

print(
    f"Bereits zugeordnet     : "
    f"{len(df) - len(mapping):,}"
)

print()

print("Länder mit den meisten offenen Ligen:")

print(

    mapping["country"]

    .value_counts()

    .head(20)

)

# =====================================================
# Fertig
# =====================================================

print()

print("=" * 70)
print("DATEI GESPEICHERT")
print("=" * 70)

print()

print(OUTPUT)

print()

print(
    "Öffne die Excel-Datei und ergänze die fehlenden"
)

print(
    "Spalten 'league_group' und 'level'."
)

print()

print("=" * 70)
