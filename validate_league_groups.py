import pandas as pd

# =====================================================
# Dateien
# =====================================================

INPUT = "output/league_groups.csv"

# =====================================================
# Laden
# =====================================================

df = pd.read_csv(
    INPUT,
    encoding="utf-8-sig"
)

print()
print("=" * 70)
print("LEAGUE GROUP VALIDATION")
print("=" * 70)

# =====================================================
# Statistik
# =====================================================

print(f"Ligen gesamt : {len(df):,}")

print()

# =====================================================
# Fehlende Werte
# =====================================================

for column in [

    "league",

    "league_group",

    "category",

    "level",

    "country",

]:

    missing = (

        df[column]

        .isna()

        .sum()

    )

    empty = (

        df[column]

        .astype(str)

        .str.strip()

        .eq("")

        .sum()

    )

    print(

        f"{column:<15}"

        f"Missing: {missing:<4}"

        f"Empty: {empty}"

    )

# =====================================================
# Doppelte Ligen
# =====================================================

duplicates = (

    df

    .duplicated(

        subset="league"

    )

)

print()

print(

    "Doppelte Ligen:",

    duplicates.sum()

)

if duplicates.any():

    print()

    print(

        df.loc[duplicates]

        .sort_values("league")

    )

# =====================================================
# Kategorien
# =====================================================

print()

print("=" * 70)
print("KATEGORIEN")
print("=" * 70)

print(

    df["category"]

    .fillna("")

    .value_counts()

)

# =====================================================
# Levels
# =====================================================

print()

print("=" * 70)
print("LEVELS")
print("=" * 70)

print(

    df["level"]

    .fillna("")

    .value_counts()

)

# =====================================================
# Fehlende league_group
# =====================================================

missing_groups = (

    df[

        df["league_group"]

        .isna()

        |

        (

            df["league_group"]

            .astype(str)

            .str.strip()

            == ""

        )

    ]

)

if len(missing_groups):

    print()

    print("=" * 70)
    print("OHNE LEAGUE GROUP")
    print("=" * 70)

    for league in missing_groups["league"]:

        print(league)

# =====================================================
# Fehlende Kategorie
# =====================================================

missing_cat = (

    df[

        df["category"]

        .isna()

        |

        (

            df["category"]

            .astype(str)

            .str.strip()

            == ""

        )

    ]

)

if len(missing_cat):

    print()

    print("=" * 70)
    print("OHNE KATEGORIE")
    print("=" * 70)

    for league in missing_cat["league"]:

        print(league)

# =====================================================
# Fehlendes Level
# =====================================================

missing_level = (

    df[

        df["level"]

        .isna()

        |

        (

            df["level"]

            .astype(str)

            .str.strip()

            == ""

        )

    ]

)

if len(missing_level):

    print()

    print("=" * 70)
    print("OHNE LEVEL")
    print("=" * 70)

    for league in missing_level["league"]:

        print(league)

print()

print("=" * 70)
print("VALIDIERUNG ABGESCHLOSSEN")
print("=" * 70)
