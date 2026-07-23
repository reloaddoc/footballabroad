import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import read_table, write_table


def build():
    master = read_table("master_dataset")

    corridors = (
        master
        .groupby(
            [
                "from_club_name",
                "from_country_name",
                "from_aggregation",
                "to_country_name",
                "to_aggregation",
            ],
            dropna=False,
            observed=False,
        )
        .agg(
            transfers=("player_id", "size"),
            unique_players=("player_id", "nunique"),
            average_age_departure=("age", "mean"),
            average_market_value_departure=("market_value", "mean"),
            top_destination_club=("to_club_name", lambda x: x.mode(
            ).iat[0] if not x.mode().empty else None),
        )
        .reset_index()
        .rename(
            columns={
                "from_club_name": "club",
                "from_country_name": "country",
                "from_aggregation": "league",
                "to_country_name": "destination_country",
                "to_aggregation": "destination_league",
            }
        )
        .sort_values(
            ["transfers", "unique_players"],
            ascending=False,
        )
        .reset_index(drop=True)
    )

    write_table("club_export_corridors", corridors)


if __name__ == "__main__":
    build()
