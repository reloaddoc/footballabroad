import re


def translate_league_name(name: str) -> str:
    """Translates German division numbering and league phases into clean English."""
    if not isinstance(name, str):
        return name

    # Translate division numbering
    name = re.sub(r"\b1\.Division\b", "1st Division", name)
    name = re.sub(r"\b2\.Division\b", "2nd Division", name)
    name = re.sub(r"\b3\.Division\b", "3rd Division", name)
    name = re.sub(r"\b4\.Division\b", "4th Division", name)

    # Translate league phases (with cleaner parenthetical format)
    name = name.replace(" Abstiegsrunde", " (Relegation Round)")
    name = name.replace(" Aufstiegsrunde", " (Promotion Round)")
    name = name.replace(" Meisterrunde", " (Championship Round)")
    name = name.replace(" Qualifikationsrunde", " (Qualification Round)")

    return name
