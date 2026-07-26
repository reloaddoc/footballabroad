import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import DB_PATH


PLAYER_LINK_SQL = """
'https://www.transfermarkt.com' ||
regexp_replace(
    relative_url,
    '/transfers/spieler/([0-9]+)(/transfer_id/[0-9]+)?',
    '/profil/spieler/\\1'
)
"""


def ensure_column(con, table_name: str, column_name: str, column_type: str) -> None:
    columns = {
        row[1]
        for row in con.execute(f"PRAGMA table_info('{table_name}')").fetchall()
    }
    if column_name not in columns:
        con.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def main() -> None:
    con = duckdb.connect(DB_PATH)
    try:
        ensure_column(con, "player_profiles", "player_link", "VARCHAR")
        con.execute(
            f"""
            UPDATE player_profiles p
            SET player_link = t.player_link
            FROM (
                SELECT
                    player_id,
                    MIN({PLAYER_LINK_SQL}) AS player_link
                FROM transfers
                WHERE relative_url IS NOT NULL
                  AND relative_url LIKE '%/transfers/spieler/%'
                GROUP BY player_id
            ) t
            WHERE p.player_id = t.player_id
            """
        )

        ensure_column(con, "master_dataset", "player_link", "VARCHAR")
        con.execute(
            f"""
            UPDATE master_dataset
            SET player_link = {PLAYER_LINK_SQL}
            WHERE relative_url IS NOT NULL
              AND relative_url LIKE '%/transfers/spieler/%'
            """
        )
    finally:
        con.close()


if __name__ == "__main__":
    main()
