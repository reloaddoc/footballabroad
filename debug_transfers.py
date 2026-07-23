from database import read_table

cp = read_table("club_profiles")

print(
    cp.loc[
        cp["club_id"].astype(str).isin(["4896", "18324"]),
        [
            "club_id",
            "name",
            "league",
            "league_code",
            "league_level",
            "league_country",
        ],
    ].to_string(index=False)
)
