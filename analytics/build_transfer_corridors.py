import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# isort: split

from database import read_table, write_table


def build():
    master = read_table("master_dataset")

    corridors = (
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
            transfers=("player_id", "size"),
            average_age=("age", "mean"),
            average_fee=("fee", "mean"),
            domestic_share=("domestic_transfer", "mean"),
            international_share=("international", "mean"),
            unique_players=("player_id", "nunique"),
            unique_agents=("agent", "nunique"),
            first_transfer_year=("date", lambda values: values.dt.year.min()),
            last_transfer_year=("date", lambda values: values.dt.year.max()),
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
        .sort_values("transfers", ascending=False)
        .reset_index(drop=True)
    )

    write_table("transfer_corridors", corridors)


if __name__ == "__main__":
    build()
