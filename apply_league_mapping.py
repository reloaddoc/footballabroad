from country_mapping import COUNTRY_MAP
from pathlib import Path

import pandas as pd

# =====================================================
# Dateien
# =====================================================

DIMENSION = "output/league_dimension.csv"

MAPPING = "output/league_mapping.xlsx"

OUTPUT = "output/league_dimension.csv"

# =====================================================
# Laden
# =====================================================

dimension = pd.read_csv(
    DIMENSION,
    encoding="utf-8-sig",
)

mapping = pd.read_excel(
    MAPPING,
)

print()

print("=" * 70)
print("APPLY LEAGUE MAPPING")
print("=" * 70)

print()

print(f"{len(dimension):,} Ligen geladen.")

print(f"{len(mapping):,} Mapping-Zeilen geladen.")
# =====================================================
# Mapping anwenden
# =====================================================

# =====================================================
# Mapping anwenden
# =====================================================

updates = 0

for _, row in mapping.iterrows():

    code = row["competition_code"]

    # =====================================================
    # HIER GEHÖRT DIE ABSICHERUNG HIN!
    # =====================================================
    if pd.isna(code):
        continue

    mask = (
        dimension["competition_code"] == code
    )

    if not mask.any():
        continue

    fields = [
        "league_group",
        "level",
        "category",
        "is_professional",
        "notes",
    ]

    # optionale Felder
    for field in [

        "is_youth",

        "is_reserve",

    ]:

        if field in mapping.columns:
            fields.append(field)

    for field in fields:

        if field not in mapping.columns:
            continue

        value = row[field]

        if pd.notna(value):

            dimension.loc[mask, field] = value

    updates += 1

    # =====================================================
# Automatische Fallback-Gruppierung
# =====================================================

AUTO_RULES = [

    # Deutschland
    (
        ["Regionalliga"],
        "Germany - Regionalliga",
        4,
        "Senior",
    ),

    (
        ["Bayernliga"],
        "Germany - Bayernliga",
        5,
        "Senior",
    ),

    (
        ["NOFV-Oberliga", "Oberliga"],
        "Germany - Oberliga",
        5,
        "Senior",
    ),

    (
        ["Verbandsliga"],
        "Germany - Verbandsliga",
        6,
        "Senior",
    ),

    (
        ["Landesliga"],
        "Germany - Landesliga",
        7,
        "Senior",
    ),

    # England
    (
        [
            "National League North",
            "National League South",
        ],
        "England - National League",
        6,
        "Senior",
    ),

    # Österreich
    (
        [
            "Regionalliga Ost",
            "Regionalliga Mitte",
            "Regionalliga West",
        ],
        "Austria - Regionalliga",
        3,
        "Senior",
    ),
]

for keywords, group, level, category in AUTO_RULES:

    mask = (
        dimension["league_group"].isna()
        | (dimension["league_group"] == "")
    )

    for keyword in keywords:

        idx = (
            mask
            & dimension["league"]
            .str.contains(keyword, case=False, na=False)
        )

        dimension.loc[idx, "league_group"] = group
        dimension.loc[idx, "level"] = level
        dimension.loc[idx, "category"] = category
        dimension.loc[idx, "is_professional"] = True

# =====================================================
# Speichern
# =====================================================

dimension = dimension.sort_values(
    [
        "country",
        "league",
    ]
).reset_index(drop=True)

# =====================================================
# Ländernamen vereinheitlichen
# =====================================================

dimension["country"] = (
    dimension["country"]
    .replace(COUNTRY_MAP)
)

# =====================================================
# Nur den Ländernamen in league_group ersetzen
# =====================================================

for de, en in COUNTRY_MAP.items():

    dimension["league_group"] = (

        dimension["league_group"]

        .fillna("")

        .str.replace(

            f"{de} - ",

            f"{en} - ",

            regex=False,

        )

    )

dimension.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig",
)

print()

print(f"{updates:,} Ligen aktualisiert.")
# =====================================================
# Qualitätsprüfung
# =====================================================

missing_groups = (

    dimension["league_group"]

    .fillna("")

    .eq("")

    .sum()

)

missing_levels = (

    dimension["level"]

    .isna()

    .sum()

)

print()

print("=" * 70)
print("QUALITÄTSPRÜFUNG")
print("=" * 70)

print()

print(f"Fehlende League Groups : {missing_groups:,}")

print(f"Fehlende Levels        : {missing_levels:,}")

print()

print("Kategorien:")

print(

    dimension["category"]

    .fillna("")

    .value_counts()

)

print()

print("Professional:")

print(

    dimension["is_professional"]

    .value_counts()

)

# =====================================================
# Vorschau
# =====================================================

print()

print("=" * 70)
print("VORSCHAU")
print("=" * 70)

print()

print(

    dimension[

        [

            "country",

            "league",

            "league_group",

            "level",

            "category",

        ]

    ]

    .head(20)

)

# =====================================================
# Fertig
# =====================================================

print()

print("=" * 70)
print("LEAGUE DIMENSION AKTUALISIERT")
print("=" * 70)

print()

print(f"Datei gespeichert: {OUTPUT}")

print("=" * 70)
