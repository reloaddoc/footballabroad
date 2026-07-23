from pathlib import Path
import json


def load_knowledge(country):
    """
    Load editorial destination knowledge from knowledge/<country>.json
    """

    path = Path("knowledge") / f"{country}.json"

    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
