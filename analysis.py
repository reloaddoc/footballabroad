import pandas as pd

# ==========================================================
# Daten laden
# ==========================================================

transfers = pd.read_csv(
    "output/transfers.csv",
    encoding="utf-8-sig"
)

clubs = pd.read_csv(
    "output/clubs.csv",
    encoding="utf-8-sig"
)

# ==========================================================
# Datentypen vereinheitlichen
# ==========================================================

transfers["from_club"] = transfers["from_club"].astype(str)
transfers["to_club"] = transfers["to_club"].astype(str)

clubs["club_id"] = clubs["club_id"].astype(str)

# ==========================================================
# Duplikate entfernen
# ==========================================================

print("=" * 60)
print("DATENQUALITÄT")
print("=" * 60)

print("Transfers vorher:", len(transfers))

transfers = transfers.drop_duplicates()

print("Transfers nachher:", len(transfers))

print()

# ==========================================================
# Vereinsnamen ergänzen
# ==========================================================

club_lookup = clubs[["club_id", "name"]].rename(
    columns={
        "club_id": "from_club",
        "name": "from_name"
    }
)

transfers = transfers.merge(
    club_lookup,
    on="from_club",
    how="left"
)

club_lookup = clubs[["club_id", "name"]].rename(
    columns={
        "club_id": "to_club",
        "name": "to_name"
    }
)

transfers = transfers.merge(
    club_lookup,
    on="to_club",
    how="left"
)

transfers["from_name"] = transfers["from_name"].fillna("Unbekannt")
transfers["to_name"] = transfers["to_name"].fillna("Unbekannt")

# ==========================================================
# Übersicht
# ==========================================================

print("=" * 60)
print("ÜBERSICHT")
print("=" * 60)

print(f"Transfers:        {len(transfers):,}")
print(f"Spieler:          {transfers['player_id'].nunique():,}")
print(f"Ausgangsvereine:  {transfers['from_club'].nunique():,}")
print(f"Zielvereine:      {transfers['to_club'].nunique():,}")

print()

# ==========================================================
# Internationale Transfers
# ==========================================================

international = transfers[
    transfers["from_country"] != transfers["to_country"]
].copy()

print("=" * 60)
print("INTERNATIONALE TRANSFERS")
print("=" * 60)

print(len(international))
print()

# ==========================================================
# Top Ausgangsvereine
# ==========================================================

print("=" * 60)
print("TOP 25 AUSGANGSVEREINE")
print("=" * 60)

print(
    international["from_name"]
    .value_counts()
    .head(25)
)

print()

# ==========================================================
# Top Zielvereine
# ==========================================================

print("=" * 60)
print("TOP 25 ZIELVEREINE")
print("=" * 60)

print(
    international["to_name"]
    .value_counts()
    .head(25)
)

print()

# ==========================================================
# Länder
# ==========================================================

print("=" * 60)
print("TOP HERKUNFTSLÄNDER")
print("=" * 60)

print(
    international["from_country"]
    .value_counts()
    .head(20)
)

print()

print("=" * 60)
print("TOP ZIELLÄNDER")
print("=" * 60)

print(
    international["to_country"]
    .value_counts()
    .head(20)
)

print()

# ==========================================================
# Alter
# ==========================================================

print("=" * 60)
print("ALTER")
print("=" * 60)

print(
    international["age"].describe()
)

print()

# ==========================================================
# Marktwert
# ==========================================================

print("=" * 60)
print("MARKTWERT")
print("=" * 60)

mv = international["market_value"].dropna()

print(mv.describe())

print()

print("Median Marktwert:", mv.median())
print("Ø Marktwert:", round(mv.mean()))

print()

# ==========================================================
# Größte Auslandstransfers
# ==========================================================

print("=" * 60)
print("TOP 20 MARKTWERTE")
print("=" * 60)

print(

    international.sort_values(
        "market_value",
        ascending=False
    )[
        [
            "player_id",
            "from_name",
            "to_name",
            "age",
            "market_value"
        ]
    ].head(20)

)

# ==========================================================
# Export
# ==========================================================

international.to_csv(
    "output/international_transfers.csv",
    index=False,
    encoding="utf-8-sig"
)

print()
print("international_transfers.csv gespeichert.")
