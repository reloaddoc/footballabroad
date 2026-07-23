from analytics.common import most_common
from database import read_table, write_table


def build():
    master = read_table("master_dataset")
    master = master[master["agent"].notna()].copy()
    master["corridor"] = (
        master["from_country_name"].fillna("Unknown")
        + " / "
        + master["from_league"].fillna("Unknown")
        + " -> "
        + master["to_country_name"].fillna("Unknown")
        + " / "
        + master["to_league"].fillna("Unknown")
    )

    agency_networks = (
        master
        .groupby("agent", dropna=False, observed=False)
        .agg(
            clients=("player_id", "nunique"),
            transfers=("player_id", "size"),
            average_market_value=("market_value", "mean"),
            average_age=("age", "mean"),
            most_common_origin_country=("from_country_name", most_common),
            most_common_destination_country=("to_country_name", most_common),
            most_common_origin_league=("from_league", most_common),
            most_common_destination_league=("to_league", most_common),
            most_common_corridor=("corridor", most_common),
            international_transfer_share=("international", "mean"),
        )
        .reset_index()
        .sort_values("transfers", ascending=False)
        .reset_index(drop=True)
    )

    write_table("agency_networks", agency_networks)


if __name__ == "__main__":
    build()
