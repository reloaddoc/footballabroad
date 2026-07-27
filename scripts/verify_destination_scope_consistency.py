import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics_ui import add_opta_scores, calculate_destination_statistics
from database import read_table


def main() -> None:
    master = add_opta_scores(read_table("master_dataset"), read_table("league_mapping"))
    master = master[
        (master["from_aggregation"] != "DFB-Nachwuchsliga")
        & (master["to_aggregation"] != "DFB-Nachwuchsliga")
    ].copy()

    profiles = [
        ("Germany 3. Liga", master[
            (master["from_country_name"] == "Germany")
            & (master["from_aggregation"].astype(str) == "3. Liga")
        ].copy()),
        ("Career Navigator default age 20-25", master[
            master["age"].between(20, 25)
            & master["to_country_name"].notna()
            & master["to_aggregation"].notna()
        ].copy()),
    ]

    mismatches = []
    checked = 0
    for profile_name, scope in profiles:
        for (country, league), group in scope.groupby(["to_country_name", "to_aggregation"], dropna=False):
            card_stats = calculate_destination_statistics(group, master)
            report_scope = group[
                (group["to_country_name"] == country)
                & (group["to_aggregation"].astype(str) == str(league))
            ].copy()
            report_stats = calculate_destination_statistics(report_scope, master)
            checked += 1
            if card_stats["moved_up"] != report_stats["moved_up"]:
                mismatches.append(
                    {
                        "profile": profile_name,
                        "country": country,
                        "league": league,
                        "card": card_stats["moved_up"],
                        "report": report_stats["moved_up"],
                    }
                )

    print(f"checked={checked}")
    print(f"mismatches={len(mismatches)}")
    if mismatches:
        for mismatch in mismatches[:20]:
            print(mismatch)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
