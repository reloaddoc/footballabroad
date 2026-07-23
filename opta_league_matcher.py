import os
import pandas as pd
from rapidfuzz import process, fuzz
from unidecode import unidecode

# 1. Dateipfade definieren
input_mapping_path = os.path.join("output", "league_mapping.csv")
input_opta_path = os.path.join("output", "opta_rankings.csv")
output_result_path = os.path.join("output", "matched_leagues.csv")

print("Lade Daten...")
df_our = pd.read_csv(input_mapping_path, encoding="utf-8")

# Robusterer und flexiblerer Parser für die Opta-Datei


def load_opta_safely(filepath):
    for delimiter in [',', ';', '\t']:
        try:
            df = pd.read_csv(filepath, sep=delimiter,
                             encoding="utf-8", dtype=str)
            if df.shape[1] > 1:
                print(
                    f"-> opta_rankings.csv erfolgreich geladen (Trennzeichen: '{delimiter}')")
                return df
        except Exception:
            continue

    print("-> Standard-Parser fehlgeschlagen. Starte zeilenweise Reparatur...")
    with open(filepath, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        sep = ';' if ';' in first_line else (
            '\t' if '\t' in first_line else ',')
        header = first_line.split(sep)

        data = []
        for line in f:
            parts = line.strip().split(sep)
            if len(parts) == len(header):
                data.append(parts)
            else:
                padded = (parts + [None] * len(header))[:len(header)]
                data.append(padded)

    return pd.DataFrame(data, columns=header)


df_opta = load_opta_safely(input_opta_path)

# Spaltennamen-Mapping für Opta dynamisch ermitteln
country_col = next((c for col in df_opta.columns if (c := col).lower() in [
                   'country', 'countryname']), df_opta.columns[2])
league_col = next((c for col in df_opta.columns if (c := col).lower() in [
                  'league', 'leaguename']), df_opta.columns[1])
rank_col = next((c for col in df_opta.columns if (c := col).lower() in [
                'rank', 'globalrank']), df_opta.columns[0])
score_col = next((c for col in df_opta.columns if (c := col).lower() in [
                 'score', 'overall score', 'seasonaveragerating']), df_opta.columns[-1])

# Erweitertes Wörterbuch für landesspezifische Fußball-Begriffe
TRANSLATION_MAP = {
    "primera": "first",
    "segunda": "second",
    "divisio": "division",
    "divisione": "division",
    "liga": "league",
    "npl": "national premier league",
    "kategoria": "division",
    "pare": "first",
    "superiore": "superiore",
    "1st": "first",
    "2nd": "second",
    "3rd": "third",
    "4th": "fourth"
}


def clean_and_translate(text):
    if not isinstance(text, str):
        return ""
    text = unidecode(text).lower().strip()
    text = text.replace(" e ", " ")
    words = text.split()
    translated_words = [TRANSLATION_MAP.get(
        w, w) for words_chunk in words for w in [words_chunk]]
    return " ".join(translated_words)


print("Normalisiere und übersetze Ligen...")
df_our['clean_country'] = df_our['country'].astype(
    str).apply(lambda x: unidecode(x).lower().strip())
df_our['clean_league'] = df_our['our_league'].apply(clean_and_translate)

df_opta['clean_country'] = df_opta[country_col].astype(
    str).apply(lambda x: unidecode(x).lower().strip())
df_opta['clean_league'] = df_opta[league_col].astype(
    str).apply(clean_and_translate)

print("Starte optimiertes Fuzzy-Matching...")
matched_rows = []

for idx, row in df_our.iterrows():
    current_country = row['clean_country']
    current_league = row['clean_league']

    opta_subset = df_opta[
        (df_opta['clean_country'] == current_country) |
        (df_opta['clean_country'].str.contains(current_country, na=False))
    ]

    if not opta_subset.empty:
        choices = opta_subset['clean_league'].tolist()
        best_match = process.extractOne(
            current_league, choices, scorer=fuzz.token_sort_ratio)

        if best_match:
            matched_text, score, match_idx = best_match
            original_opta_row = opta_subset.iloc[match_idx]

            result_entry = row.to_dict()
            result_entry.update({
                'opta_leagueName': original_opta_row[league_col],
                'opta_globalRank': original_opta_row[rank_col],
                'opta_seasonAverageRating': original_opta_row[score_col],
                'match_confidence': round(score, 1)
            })
            matched_rows.append(result_entry)
    else:
        result_entry = row.to_dict()
        result_entry.update({
            'opta_leagueName': None,
            'opta_globalRank': None,
            'opta_seasonAverageRating': None,
            'match_confidence': 0
        })
        matched_rows.append(result_entry)

df_result = pd.DataFrame(matched_rows)

# Daten zurück in Zahlen konvertieren
df_result['opta_globalRank'] = pd.to_numeric(
    df_result['opta_globalRank'], errors='coerce')
df_result['opta_seasonAverageRating'] = pd.to_numeric(
    df_result['opta_seasonAverageRating'], errors='coerce')

# Grenze auf 70.0 gesenkt, um Bundesliga (74.1) zu retten, aber Amateure (<64) zu loeschen
low_conf_mask = df_result['match_confidence'] < 70.0
df_result.loc[low_conf_mask, ['opta_leagueName',
                              'opta_globalRank', 'opta_seasonAverageRating']] = None

# Hilfsspalten entfernen
cols_to_drop = ['clean_country', 'clean_league', 'opta_league',
                'opta_country', 'opta_rank', 'opta_score', 'match_method', 'match_score']
df_result = df_result.drop(
    columns=[c for c in cols_to_drop if c in df_result.columns])

# Speichern
df_result.to_csv(output_result_path, index=False, encoding="utf-8-sig")
print(f"Abgeschlossen! Datei sauber gespeichert unter '{output_result_path}'.")
