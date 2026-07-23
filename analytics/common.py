import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def most_common(series):
    values = series.dropna()
    values = values[values.astype(str).str.strip() != ""]
    if values.empty:
        return None
    return values.mode().iloc[0]


def age_bucket(age):
    if pd.isna(age):
        return "Unknown"
    age = int(age)
    if age <= 18:
        return "18 or younger"
    if age <= 20:
        return "19-20"
    if age <= 23:
        return "21-23"
    if age <= 26:
        return "24-26"
    if age <= 30:
        return "27-30"
    return "31+"


def league_level_bucket(level):
    if pd.isna(level):
        return "Unknown"
    level = int(level)
    if level == 1:
        return "First Division"
    if level == 2:
        return "Second Division"
    if level == 3:
        return "Third Division"
    if level == 4:
        return "Fourth Division"
    return "Lower Division"
