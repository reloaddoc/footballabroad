import pandas as pd

df = pd.read_csv(
    "output/master_dataset.csv",
    encoding="utf-8-sig"
)

leagues = sorted(
    set(
        pd.concat([
            df["from_league"],
            df["to_league"]
        ])
        .dropna()
    )
)

out = pd.DataFrame({

    "league": leagues,

    "league_group": leagues,

    "level": "",

    "category": "",

    "country": ""

})

out.to_csv(

    "output/league_groups.csv",

    index=False,

    encoding="utf-8-sig"

)

print(len(out), "Ligen exportiert.")
