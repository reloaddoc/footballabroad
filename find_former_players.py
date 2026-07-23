import pandas as pd

df = pd.read_csv("output/master_dataset.csv")

# Nur die letzte Station jedes Spielers
latest = (
    df.sort_values("date")
      .groupby("player_id", as_index=False)
      .last()
)

# Filter (Korrekt mit '&' statt Komma)
former = latest[
    (latest["age"] >= 30) &
    (latest["age"] <= 34) &
    (latest["international_moves"] >= 1)
]

# Interessante Spalten
former = former[
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

former = former.sort_values(
    ["age", "international_moves"],
    ascending=[False, False]
)

former.to_csv(
    "output/former_players.csv",
    index=False,
    encoding="utf-8-sig",
)

print(f"{len(former)} players exported.")
