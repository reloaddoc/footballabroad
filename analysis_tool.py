import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

df = pd.read_csv(
    "output/master_dataset.csv",
    encoding="utf-8-sig"
)

# --------------------------------------------------------


def dashboard():

    print("\n================ DASHBOARD ================\n")

    print(f"Transfers:        {len(df):,}")
    print(f"Spieler:          {df.player_id.nunique():,}")
    print(f"Agenturen:        {df.agent.nunique():,}")
    print(f"Vereine:          {df.from_club_name.nunique():,}")
    print(f"Länder:           {df.to_country.nunique():,}")
    print(f"Internationale:   {df['international'].sum():,}")

    print()

    print("Top Zielländer")

    print(
        df["to_country"]
        .value_counts()
        .head(15)
    )

# --------------------------------------------------------


def analyse_country():

    country = input("\nLändercode eingeben: ")

    x = df[
        df["to_country"].astype(str) == country
    ]

    print()

    print(f"Transfers: {len(x)}")

    print()

    print("Top Herkunftsländer")

    print(
        x["from_country"]
        .value_counts()
        .head(10)
    )

    print()

    print("Top Herkunftsligen")

    print(
        x["from_competition"]
        .value_counts()
        .head(10)
    )

    print()

    print("Top Agenturen")

    print(
        x["agent"]
        .value_counts()
        .head(15)
    )

    print()

    print("Top Vereine")

    print(
        x["to_club_name"]
        .value_counts()
        .head(20)
    )

# --------------------------------------------------------


def analyse_agent():

    name = input("\nAgentur: ")

    x = df[
        df["agent"]
        .fillna("")
        .str.contains(
            name,
            case=False
        )
    ]

    if len(x) == 0:

        print("Keine Treffer")

        return

    print()

    print(f"Transfers: {len(x)}")

    print()

    print("Spieler")

    print(
        x["full_name"]
        .drop_duplicates()
        .sort_values()
        .to_string(index=False)
    )

    print()

    print("Zielländer")

    print(
        x["to_country"]
        .value_counts()
    )

    print()

    print("Zielvereine")

    print(
        x["to_club_name"]
        .value_counts()
        .head(20)
    )

# --------------------------------------------------------


def analyse_club():

    club = input("\nVerein: ")

    x = df[
        df["to_club_name"]
        .fillna("")
        .str.contains(
            club,
            case=False
        )
    ]

    if len(x) == 0:

        print("Keine Treffer")

        return

    print()

    print(x[
        [
            "full_name",
            "from_club_name",
            "to_club_name",
            "market_value",
            "age",
            "agent",
            "position"
        ]
    ])

# --------------------------------------------------------


def analyse_player():

    name = input("\nSpieler: ")

    x = df[
        df["full_name"]
        .fillna("")
        .str.contains(
            name,
            case=False
        )
    ]

    if len(x) == 0:

        print("Nicht gefunden")

        return

    print()

    print(x[
        [
            "date",
            "from_club_name",
            "to_club_name",
            "market_value",
            "career_path"
        ]
    ])

# --------------------------------------------------------


def top_transfers():

    x = df.sort_values(
        "market_value",
        ascending=False
    )

    print()

    print(

        x[
            [
                "full_name",
                "market_value",
                "from_club_name",
                "to_club_name",
                "agent"
            ]
        ].head(30)

    )

# --------------------------------------------------------


while True:

    print()

    print("="*45)

    print("Football Abroad Intelligence")

    print("="*45)

    print("1 Dashboard")

    print("2 Länder")

    print("3 Vereine")

    print("4 Agenturen")

    print("5 Spieler")

    print("6 Top Transfers")

    print("0 Ende")

    choice = input("> ")

    if choice == "1":

        dashboard()

    elif choice == "2":

        analyse_country()

    elif choice == "3":

        analyse_club()

    elif choice == "4":

        analyse_agent()

    elif choice == "5":

        analyse_player()

    elif choice == "6":

        top_transfers()

    elif choice == "0":

        break
