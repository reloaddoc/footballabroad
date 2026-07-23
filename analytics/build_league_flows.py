import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import read_table, write_table


def build():
    master = read_table("master_dataset")

    league_flows = (
        master
        .groupby(
            [
                "from_country_name",
                "from_aggregation",
                "to_country_name",
                "to_aggregation",
            ],
            dropna=False,
            observed=False,
        )
        .agg(
            moves=("player_id", "size"),
            average_age=("age", "mean"),
            average_market_value=("market_value", "mean"),
            average_fee=("fee", "mean"),
            unique_players=("player_id", "nunique"),
        )
        .reset_index()
        .rename(
            columns={
                "from_country_name": "from_country",
                "from_aggregation": "from_league",
                "to_country_name": "to_country",
                "to_aggregation": "to_league",
            }
        )
        .sort_values("moves", ascending=False)
        .reset_index(drop=True)
    )

    write_table("league_flows", league_flows)


if __name__ == "__main__":
    build()