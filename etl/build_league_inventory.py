from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from database import read_table, write_table

LEAGUE_DIMENSION = "league_dimension"

EXCEL = "league_inventory.xlsx"
CSV = "league_inventory.csv"



def main():
    # Read current league dimension from DuckDB
    dimension = read_table(LEAGUE_DIMENSION).copy()

    dimension = dimension[
        [
            "competition_code",
            "league",
            "country",
            "league_group",
            "level",
            "category",
            "is_youth",
            "is_reserve",
            "is_professional",
            "notes",
        ]
    ].drop_duplicates()

    # ---------------------------------------------------------
    # Existing inventory?
    # ---------------------------------------------------------
    if Path(EXCEL).exists():
        inventory = pd.read_excel(EXCEL)

        # ensure same columns
        for col in dimension.columns:
            if col not in inventory.columns:
                inventory[col] = pd.NA

        if "aggregation" not in inventory.columns:
            inventory["aggregation"] = pd.NA

        # Add new leagues only
        existing = set(inventory["competition_code"].astype(str))

        new_rows = dimension[
            ~dimension["competition_code"].astype(str).isin(existing)
        ].copy()

        if not new_rows.empty:
            new_rows["aggregation"] = pd.NA
            inventory = pd.concat(
                [inventory, new_rows],
                ignore_index=True,
            )

    else:
        inventory = dimension.copy()
        inventory["aggregation"] = pd.NA

    # ---------------------------------------------------------
    # Clean up
    # ---------------------------------------------------------
    inventory = inventory.sort_values(
        ["country", "level", "league"],
        na_position="last",
    ).reset_index(drop=True)

    
    # ---------------------------------------------------------
    # Ensure one row per competition_code
    # ---------------------------------------------------------

    inventory = inventory[inventory["competition_code"].notna()].copy()

    inventory = (  
        inventory
         .sort_values(["competition_code", "league"])
         .drop_duplicates(subset=["competition_code"], keep="first")
         .reset_index(drop=True)
    )	

    # ---------------------------------------------------------
    # Save Excel
    # ---------------------------------------------------------
    inventory.to_excel(EXCEL, index=False)

    # ---------------------------------------------------------
    # Save CSV
    # ---------------------------------------------------------
    inventory.to_csv(
        CSV,
        index=False,
        encoding="utf-8-sig",
    )

    # ---------------------------------------------------------
    # Update DuckDB
    # ---------------------------------------------------------
    write_table("league_inventory", inventory)

    print(f"✓ {len(inventory):,} leagues written.")
    print(f"✓ Excel updated: {EXCEL}")
    print(f"✓ CSV updated: {CSV}")
    print("✓ DuckDB table 'league_inventory' updated.")


if __name__ == "__main__":
    main()