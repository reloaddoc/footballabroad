import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import DB_PATH


def main() -> None:
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        summary = con.execute(
            """
            SELECT
                COUNT(*) AS rows,
                COUNT(player_link) AS linked_rows,
                COUNT(DISTINCT player_id) AS players,
                COUNT(DISTINCT CASE WHEN player_link IS NOT NULL THEN player_id END) AS linked_players
            FROM master_dataset
            """
        ).fetchdf()

        examples = con.execute(
            """
            SELECT player_id, full_name, player_link
            FROM master_dataset
            WHERE full_name IN ('Jakob Tranziska', 'Dominik Friedrich Schad')
            GROUP BY player_id, full_name, player_link
            ORDER BY full_name
            """
        ).fetchdf()

        master_columns = con.execute(
            """
            SELECT name, type
            FROM pragma_table_info('master_dataset')
            WHERE name IN ('relative_url', 'player_link')
            ORDER BY name
            """
        ).fetchdf()

        profile_columns = con.execute(
            """
            SELECT name, type
            FROM pragma_table_info('player_profiles')
            WHERE name = 'player_link'
            """
        ).fetchdf()
    finally:
        con.close()

    text = (
        "MASTER SUMMARY\n"
        + summary.to_string(index=False)
        + "\n\nEXAMPLES\n"
        + examples.to_string(index=False)
        + "\n\nMASTER COLUMNS\n"
        + master_columns.to_string(index=False)
        + "\n\nPLAYER PROFILE COLUMNS\n"
        + profile_columns.to_string(index=False)
    )
    print(text.encode("ascii", "backslashreplace").decode("ascii"))


if __name__ == "__main__":
    main()
