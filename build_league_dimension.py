from country_mapping import COUNTRY_MAP
from pathlib import Path

import pandas as pd

# =====================================================
# Dateien
# =====================================================

MASTER = "output/master_dataset.csv"

OUTPUT = "output/league_dimension.csv"

Path("output").mkdir(exist_ok=True)

# =====================================================
# Laden
# =====================================================

df = pd.read_csv(
    MASTER,
    encoding="utf-8-sig",
    low_memory=False,
)

print()
print("=" * 70)
print("BUILD LEAGUE DIMENSION")
print("=" * 70)
print()

print(f"{len(df):,} Transfers geladen.")

# =====================================================
# Hilfsfunktion
# =====================================================


def extract_side(
    frame,
    league_col,
    code_col,
    country_col,
):

    data = frame[
        [
            league_col,
            code_col,
            country_col,
        ]
    ].copy()

    data.columns = [

        "league",

        "competition_code",

        "country",

    ]

    data = data.dropna(
        subset=["league"]
    )

    return data

# =====================================================
# FROM
# =====================================================


from_df = extract_side(

    df,

    "from_league",

    "from_league_code",

    "from_country_name",

)

# =====================================================
# TO
# =====================================================

to_df = extract_side(

    df,

    "to_league",

    "to_league_code",

    "to_country_name",

)

# =====================================================
# Zusammenführen
# =====================================================

leagues = pd.concat(

    [

        from_df,

        to_df,

    ],

    ignore_index=True,

)
# =====================================================
# Häufigstes Land pro Liga
# =====================================================

country_lookup = (

    leagues

    .groupby("league")["country"]

    .agg(

        lambda x: x.dropna().mode().iloc[0]

        if len(x.dropna()) > 0

        else None

    )

)


# =====================================================
# Häufigster Competition Code pro Liga
# =====================================================

code_lookup = (

    leagues

    .groupby("league")["competition_code"]

    .agg(

        lambda x: x.dropna().mode().iloc[0]

        if len(x.dropna()) > 0

        else None

    )

)

# =====================================================
# League Dimension erzeugen
# =====================================================

dimension = pd.DataFrame({

    "league": country_lookup.index,

    "competition_code": code_lookup.values,

    "country": country_lookup.values,

})


dimension["country"] = (
    dimension["country"]
    .replace(COUNTRY_MAP)
)

# =====================================================
# Zusätzliche Stammdatenfelder
# =====================================================

dimension["league_group"] = ""

dimension["level"] = pd.NA

dimension["category"] = ""

dimension["is_youth"] = False

dimension["is_reserve"] = False

dimension["is_professional"] = pd.NA

dimension["notes"] = ""

# =====================================================
# Sortieren
# =====================================================

dimension = (

    dimension

    .sort_values(

        [

            "country",

            "league",

        ],

        na_position="last",

    )

    .reset_index(

        drop=True

    )

)

print()

print(

    f"{len(dimension):,} eindeutige Ligen gefunden."

)
# =====================================================
# Qualitätsprüfungen
# =====================================================

print()

print("=" * 70)
print("QUALITÄTSPRÜFUNG")
print("=" * 70)

print()

print(
    "Fehlende Competition Codes :",
    dimension["competition_code"].isna().sum()
)

print(
    "Fehlende Länder           :",
    dimension["country"].isna().sum()
)

print(
    "Doppelte Ligen           :",
    dimension["league"].duplicated().sum()
)

# =====================================================
# Speichern
# =====================================================

dimension.to_csv(

    OUTPUT,

    index=False,

    encoding="utf-8-sig"

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

            "competition_code",

            "league",

            "country",

        ]

    ]

    .head(20)

)

# =====================================================
# Statistik
# =====================================================

print()

print("=" * 70)
print("LEAGUE DIMENSION")
print("=" * 70)

print(f"Ligen gesamt            : {len(dimension):,}")

print(
    f"Competition Codes       : "
    f"{dimension['competition_code'].notna().sum():,}"
)

print(
    f"Länder                  : "
    f"{dimension['country'].nunique():,}"
)

print()

print("Top Länder:")

print(

    dimension["country"]

    .value_counts()

    .head(20)

)

print()

print("Gespeichert:")

print(OUTPUT)

print("=" * 70)
