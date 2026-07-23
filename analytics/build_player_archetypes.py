from analytics.common import age_bucket, league_level_bucket, most_common
from database import read_table, write_table


def build():
    master = read_table("master_dataset")
    master = master.copy()

    master["age_bucket"] = master["age"].apply(age_bucket)
    master["league_level"] = master["from_league_level"].apply(
        league_level_bucket)

    player_archetypes = (
        master
        .groupby(
            [
                "primary_nationality",
                "age_bucket",
                "league_level",
            ],
            dropna=False,
            observed=False,
        )
        .agg(
            number_of_players=("player_id", "nunique"),
            transfers=("player_id", "size"),
            most_common_next_country=("to_country_name", most_common),
            most_common_next_league=("to_league", most_common),
            most_common_next_club=("to_club_name", most_common),
            average_transfer_fee=("fee", "mean"),
            average_age=("age", "mean"),
            international_share=("international", "mean"),
        )
        .reset_index()
        .sort_values(["number_of_players", "transfers"], ascending=False)
        .reset_index(drop=True)
    )

    write_table("player_archetypes", player_archetypes)


if __name__ == "__main__":
    build()
