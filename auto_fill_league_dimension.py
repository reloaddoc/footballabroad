import pandas as pd

# =====================================================
# Dateien
# =====================================================

INPUT = "output/league_dimension.csv"

# =====================================================
# Laden
# =====================================================

df = pd.read_csv(
    INPUT,
    encoding="utf-8-sig"
)

print(f"{len(df):,} Ligen geladen.")

# -----------------------------------------------------
# Datentypen
# -----------------------------------------------------

for col in [

    "league_group",

    "category",

    "country",

    "level",

]:

    df[col] = df[col].astype("object")

# =====================================================
# Hilfsfunktion
# =====================================================


def fill(row, rule):

    row["league_group"] = rule["group"]
    row["category"] = rule["category"]
    row["level"] = rule["level"]

    return row

# =====================================================
# Regeln
# =====================================================


RULES = [

    # -------------------------------------------------
    # Deutschland
    # -------------------------------------------------

    {
        "contains": ["Regionalliga"],
        "group": "Germany - Regionalliga",
        "country": "Germany",
        "level": 4,
        "category": "Senior",
    },

    {
        "contains": ["NOFV-Oberliga", "Oberliga"],
        "group": "Germany - Oberliga",
        "country": "Germany",
        "level": 5,
        "category": "Senior",
    },

    {
        "contains": ["Verbandsliga"],
        "group": "Germany - Verbandsliga",
        "country": "Germany",
        "level": 6,
        "category": "Senior",
    },

    {
        "contains": ["Landesliga"],
        "group": "Germany - Landesliga",
        "country": "Germany",
        "level": 7,
        "category": "Senior",
    },

    {
        "contains": ["Bayernliga"],
        "group": "Germany - Bayernliga",
        "country": "Germany",
        "level": 5,
        "category": "Senior",
    },

    {
        "contains": ["Westfalenliga"],
        "group": "Germany - Westfalenliga",
        "country": "Germany",
        "level": 6,
        "category": "Senior",
    },

    {
        "contains": ["Bundesliga"],
        "exact": True,
        "group": "Germany - Bundesliga",
        "country": "Germany",
        "level": 1,
        "category": "Senior",
    },

    {
        "contains": ["2. Bundesliga"],
        "exact": True,
        "group": "Germany - 2. Bundesliga",
        "country": "Germany",
        "level": 2,
        "category": "Senior",
    },

    {
        "contains": ["3. Liga"],
        "exact": True,
        "group": "Germany - 3. Liga",
        "country": "Germany",
        "level": 3,
        "category": "Senior",
    },
]

# -------------------------------------------------
# Italien
# -------------------------------------------------

{
    "contains": ["Serie A"],
    "exact": True,
    "group": "Italy - Serie A",
    "country": "Italy",
    "level": 1,
    "category": "Senior",
},

{
    "contains": ["Serie B"],
    "exact": True,
    "group": "Italy - Serie B",
    "country": "Italy",
    "level": 2,
    "category": "Senior",
},

{
    "contains": ["Serie C"],
    "group": "Italy - Serie C",
    "country": "Italy",
    "level": 3,
    "category": "Senior",
},

{
    "contains": ["Serie D"],
    "group": "Italy - Serie D",
    "country": "Italy",
    "level": 4,
    "category": "Senior",
},

# -------------------------------------------------
# Spanien
# -------------------------------------------------

{
    "contains": ["LaLiga"],
    "exact": True,
    "group": "Spain - LaLiga",
    "country": "Spain",
    "level": 1,
    "category": "Senior",
},

{
    "contains": ["LaLiga2"],
    "exact": True,
    "group": "Spain - LaLiga2",
    "country": "Spain",
    "level": 2,
    "category": "Senior",
},

{
    "contains": ["Primera Federación"],
    "group": "Spain - Primera Federación",
    "country": "Spain",
    "level": 3,
    "category": "Senior",
},

{
    "contains": ["Segunda Federación"],
    "group": "Spain - Segunda Federación",
    "country": "Spain",
    "level": 4,
    "category": "Senior",
},

# -------------------------------------------------
# England
# -------------------------------------------------

{
    "contains": ["Premier League"],
    "exact": True,
    "group": "England - Premier League",
    "country": "England",
    "level": 1,
    "category": "Senior",
},

{
    "contains": ["Championship"],
    "exact": True,
    "group": "England - Championship",
    "country": "England",
    "level": 2,
    "category": "Senior",
},

{
    "contains": ["League One"],
    "exact": True,
    "group": "England - League One",
    "country": "England",
    "level": 3,
    "category": "Senior",
},

{
    "contains": ["League Two"],
    "exact": True,
    "group": "England - League Two",
    "country": "England",
    "level": 4,
    "category": "Senior",
},

{
    "contains": [
        "National League North",
        "National League South",
        "National League - North",
        "National League - South",
        "National League - Central",
        "National League",
    ],
    "group": "England - National League",
    "country": "England",
    "level": 5,
    "category": "Senior",
},

# -------------------------------------------------
# Portugal
# -------------------------------------------------

{
    "contains": ["Liga Portugal"],
    "exact": True,
    "group": "Portugal - Liga Portugal",
    "country": "Portugal",
    "level": 1,
    "category": "Senior",
},

{
    "contains": ["Liga Portugal 2"],
    "exact": True,
    "group": "Portugal - Liga Portugal 2",
    "country": "Portugal",
    "level": 2,
    "category": "Senior",
},

{
    "contains": ["Campeonato de Portugal"],
    "group": "Portugal - Campeonato de Portugal",
    "country": "Portugal",
    "level": 4,
    "category": "Senior",
},

# -------------------------------------------------
# Belgien
# -------------------------------------------------

{
    "contains": ["Jupiler Pro League"],
    "group": "Belgium - Jupiler Pro League",
    "country": "Belgium",
    "level": 1,
    "category": "Senior",
},

{
    "contains": ["Challenger Pro League"],
    "group": "Belgium - Challenger Pro League",
    "country": "Belgium",
    "level": 2,
    "category": "Senior",
},

{
    "contains": ["1ste Nationale"],
    "group": "Belgium - Nationale 1",
    "country": "Belgium",
    "level": 3,
    "category": "Senior",
},

{
    "contains": ["2de Nationale"],
    "group": "Belgium - Nationale 2",
    "country": "Belgium",
    "level": 4,
    "category": "Senior",
},

# -------------------------------------------------
# Türkei
# -------------------------------------------------

{
    "contains": ["Süper Lig"],
    "group": "Turkey - Süper Lig",
    "country": "Turkey",
    "level": 1,
    "category": "Senior",
},

{
    "contains": ["2.Lig"],
    "group": "Turkey - 2. Lig",
    "country": "Turkey",
    "level": 3,
    "category": "Senior",
},

{
    "contains": ["3.Lig"],
    "group": "Turkey - 3. Lig",
    "country": "Turkey",
    "level": 4,
    "category": "Senior",
},

# =====================================================
# Regeln anwenden
# =====================================================

matched = 0

for i, row in df.iterrows():

    league = str(row["league"]).strip()

    found = False

    # -------------------------------------------------
    # Regelwerk
    # -------------------------------------------------

    for rule in RULES:

        exact = rule.get("exact", False)

        for keyword in rule["contains"]:

            if exact:

                if league == keyword:

                    row = fill(row, rule)

                    found = True

                    break

            else:

                if keyword in league:

                    row = fill(row, rule)

                    found = True

                    break

        if found:
            break

    # -------------------------------------------------
    # Jugend
    # -------------------------------------------------

    if not found:

        youth = [

            "U15",
            "U16",
            "U17",
            "U18",
            "U19",
            "U20",
            "U21",
            "Youth",
            "Nachwuchsliga",
            "Jugendliga",
            "Drenge",
            "Junior",
            "Jgd",
            "YFL",

        ]

        if any(x in league for x in youth):

            row["category"] = "Youth"
            row["is_youth"] = True

            found = True

    # -------------------------------------------------
    # Reserve
    # -------------------------------------------------

    if not found:

        reserve = [

            "Reserve",
            "Reserves",
            "II",
            "Primavera",
            "Premier League 2",
            "Next Pro",
            "NextGen",

        ]

        if any(x in league for x in reserve):

            row["category"] = "Reserve"
            row["is_reserve"] = True

            found = True

    # -------------------------------------------------
    # Academy
    # -------------------------------------------------

    if not found:

        if "Academy" in league:

            row["category"] = "Academy"

            row["is_reserve"] = True

            found = True

    # -------------------------------------------------
    # Vereinslos
    # -------------------------------------------------

    if league == "Vereinslos":

        row["league_group"] = "Unattached"

        row["category"] = "Unattached"

        row["level"] = None

        row["is_professional"] = False

        found = True

    # -------------------------------------------------
    # Fallback
    # -------------------------------------------------

    if found:
        matched += 1

    # -------------------------------------------------
    # Professional
    # -------------------------------------------------

    if row["category"] == "Senior":

        row["is_professional"] = True

    else:

        row["is_professional"] = False

    df.loc[i] = row

# =====================================================
# Speichern
# =====================================================

df.to_csv(

    INPUT,

    index=False,

    encoding="utf-8-sig"

)

# =====================================================
# Statistik
# =====================================================

print()

print("=" * 70)
print("AUTO FILL ABGESCHLOSSEN")
print("=" * 70)

print()

print(f"Ligen gesamt      : {len(df):,}")

print(f"Automatisch erkannt: {matched:,}")

print()

print("Kategorien:")

print(

    df["category"]

    .fillna("Unbekannt")

    .value_counts()

)

print()

print("Fehlende Gruppen:")

print(

    df["league_group"]

    .isna()

    .sum()

)

print()

print("Professional:")

print(

    df["is_professional"]

    .value_counts()

)

print()

print("Youth:")

print(

    df["is_youth"]

    .value_counts()

)

print()

print("Reserve:")

print(

    df["is_reserve"]

    .value_counts()

)

print()

print("Datei gespeichert:")

print(INPUT)

print("=" * 70)
