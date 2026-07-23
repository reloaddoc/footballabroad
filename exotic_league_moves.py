import pandas as pd

df = pd.read_csv("output/master_dataset.csv")

# Zielländer
target_countries = [
    "Thailand",
    "Vietnam",
    "Malaysia",
    "Kazakhstan",
    "Uzbekistan",
    "Malta",
    "Taiwan",
    "Singapore",
    "Hong Kong",
    "Philippines",
    "Indonesia",
    "India",
]

# Europäische Nationalitäten
european_nationalities = [
    "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan",
    "Belarus", "Belgium", "Bosnia-Herzegovina", "Bulgaria",
    "Croatia", "Cyprus", "Czech Republic", "Denmark",
    "England", "Estonia", "Faroe Islands", "Finland",
    "France", "Georgia", "Germany", "Greece", "Hungary",
    "Iceland", "Ireland", "Israel", "Italy", "Kosovo",
    "Latvia", "Liechtenstein", "Lithuania", "Luxembourg",
    "Malta", "Moldova", "Montenegro", "Netherlands",
    "North Macedonia", "Northern Ireland", "Norway",
    "Poland", "Portugal", "Romania", "Russia", "San Marino",
    "Scotland", "Serbia", "Slovakia", "Slovenia", "Spain",
    "Sweden", "Switzerland", "Turkey", "Ukraine", "Wales"
]

# Spieler finden, die mindestens einmal in eines der Zielländer gewechselt sind
players = df[
    (df["to_country_name"].isin(target_countries)) &
    (df["nationality"].isin(european_nationalities))
]["player_id"].unique()

# Letzte Station dieser Spieler
latest = (
    df[df["player_id"].isin(players)]
    .sort_values("date")
    .groupby("player_id", as_index=False)
    .last()
)

# Relevante Spalten
result = latest[
    [
        "full_name",
        "age",
        "nationality",
        "current_club",
        "market_value",
        "international_moves",
        "career_length",
        "last_club",
    ]
]

result = result.sort_values(
    ["international_moves", "market_value"],
    ascending=[False, False]
)

result.to_csv(
    "output/europeans_to_exotics.csv",
    index=False,
    encoding="utf-8-sig",
)

print(f"{len(result)} players exported.")
