import pandas as pd

# ==========================================================
# Daten laden
# ==========================================================

steps = pd.read_csv(
    "output/career_steps.csv",
    encoding="utf-8-sig"
)

# ==========================================================
# Daten bereinigen
# ==========================================================

steps = steps.drop_duplicates()

steps["market_value"] = pd.to_numeric(
    steps["market_value"],
    errors="coerce"
)

steps["age"] = pd.to_numeric(
    steps["age"],
    errors="coerce"
)

# ==========================================================
# CLUB NETWORK
# ==========================================================

club_network = (
    steps
    .groupby(
        [
            "from_club",
            "to_club"
        ],
        dropna=False
    )
    .agg(

        transfers=("player_id", "count"),

        unique_players=("player_id", "nunique"),

        avg_age=("age", "mean"),

        median_market_value=("market_value", "median"),

        avg_market_value=("market_value", "mean")

    )
    .reset_index()
    .sort_values(
        "transfers",
        ascending=False
    )
)

club_network.to_csv(
    "output/club_network.csv",
    index=False,
    encoding="utf-8-sig"
)

# ==========================================================
# COMPETITION NETWORK
# ==========================================================

competition_network = (
    steps
    .groupby(
        [
            "from_competition",
            "to_competition"
        ],
        dropna=False
    )
    .agg(

        transfers=("player_id", "count"),

        unique_players=("player_id", "nunique"),

        avg_age=("age", "mean"),

        median_market_value=("market_value", "median")

    )
    .reset_index()
    .sort_values(
        "transfers",
        ascending=False
    )
)

competition_network.to_csv(
    "output/competition_network.csv",
    index=False,
    encoding="utf-8-sig"
)

# ==========================================================
# COUNTRY NETWORK
# ==========================================================

country_network = (
    steps
    .groupby(
        [
            "from_country",
            "to_country"
        ],
        dropna=False
    )
    .agg(

        transfers=("player_id", "count"),

        unique_players=("player_id", "nunique"),

        avg_age=("age", "mean"),

        median_market_value=("market_value", "median")

    )
    .reset_index()
    .sort_values(
        "transfers",
        ascending=False
    )
)

country_network.to_csv(
    "output/country_network.csv",
    index=False,
    encoding="utf-8-sig"
)

# ==========================================================
# Konsolenausgabe
# ==========================================================

print("=" * 70)
print("CAREER NETWORK ANALYSIS")
print("=" * 70)

print()

print("Club-Netzwerk")
print("-----------------------------")
print(f"Kanten: {len(club_network):,}")
print(
    f"Vereine: {len(set(club_network['from_club']) | set(club_network['to_club'])):,}"
)

print()

print("Top 20 Club-Verbindungen")
print("-----------------------------")
print(club_network.head(20))

print()

print("Competition-Netzwerk")
print("-----------------------------")
print(f"Kanten: {len(competition_network):,}")

print()

print("Top 20 Wettbewerbs-Wechsel")
print("-----------------------------")
print(competition_network.head(20))

print()

print("Country-Netzwerk")
print("-----------------------------")
print(f"Kanten: {len(country_network):,}")

print()

print("Top 20 Länder-Wechsel")
print("-----------------------------")
print(country_network.head(20))

print()

print("=" * 70)
print("Dateien gespeichert:")
print("output/club_network.csv")
print("output/competition_network.csv")
print("output/country_network.csv")
print("=" * 70)
