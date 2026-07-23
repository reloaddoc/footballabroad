import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics.common import most_common
from database import read_table, write_table


def build():
    master = read_table("master_dataset")

    stepping_clubs = (
        master
        .groupby(
            [
                "from_club_name",
                "from_country_name",
                "from_aggregation",
            ],
            dropna=False,
            observed=False,
        )
        .agg(
            international_exits=("international", "sum"),
            domestic_exits=("domestic_transfer", "sum"),
            average_age_departure=("age", "mean"),
            average_market_value_departure=("market_value", "mean"),
            top_destination_country=("to_country_name", most_common),
            top_destination_league=("to_aggregation", most_common),
            top_destination_club=("to_club_name", most_common),
            unique_destination_countries=("to_country_name", "nunique"),
            unique_destination_leagues=("to_aggregation", "nunique"),
            transfers=("player_id", "size"),
            unique_players=("player_id", "nunique"),
        )
        .reset_index()
        .rename(
            columns={
                "from_club_name": "club",
                "from_country_name": "country",
                "from_aggregation": "league",
            }
        )
        .sort_values(
            ["international_exits", "transfers"],
            ascending=False,
        )
        .reset_index(drop=True)
    )

    write_table("stepping_clubs", stepping_clubs)


if __name__ == "__main__":
    build()