"""
translations.py

Central translation dictionaries for Kickways.

Raw Transfermarkt data stays unchanged.
Translations are applied during the ETL.
"""

# ==========================================================
# COUNTRIES
# ==========================================================

COUNTRY_MAP = {
    "Deutschland": "Germany",
    "Österreich": "Austria",
    "Schweiz": "Switzerland",
    "England": "England",
    "Schottland": "Scotland",
    "Wales": "Wales",
    "Nordirland": "Northern Ireland",
    "Irland": "Ireland",
    "Frankreich": "France",
    "Spanien": "Spain",
    "Portugal": "Portugal",
    "Italien": "Italy",
    "Niederlande": "Netherlands",
    "Belgien": "Belgium",
    "Luxemburg": "Luxembourg",
    "Dänemark": "Denmark",
    "Norwegen": "Norway",
    "Schweden": "Sweden",
    "Finnland": "Finland",
    "Island": "Iceland",

    "Polen": "Poland",
    "Tschechien": "Czech Republic",
    "Slowakei": "Slovakia",
    "Ungarn": "Hungary",
    "Rumänien": "Romania",
    "Bulgarien": "Bulgaria",
    "Kroatien": "Croatia",
    "Serbien": "Serbia",
    "Bosnien-Herzegowina": "Bosnia and Herzegovina",
    "Bosnien und Herzegowina": "Bosnia and Herzegovina",
    "Slowenien": "Slovenia",
    "Montenegro": "Montenegro",
    "Nordmazedonien": "North Macedonia",
    "Kosovo": "Kosovo",
    "Albanien": "Albania",

    "Ukraine": "Ukraine",
    "Russland": "Russia",
    "Belarus": "Belarus",
    "Litauen": "Lithuania",
    "Lettland": "Latvia",
    "Estland": "Estonia",

    "Türkei": "Turkey",
    "Griechenland": "Greece",
    "Zypern": "Cyprus",

    "Georgien": "Georgia",
    "Armenien": "Armenia",
    "Aserbaidschan": "Azerbaijan",

    "Kasachstan": "Kazakhstan",
    "Usbekistan": "Uzbekistan",

    "Iran": "Iran",
    "Irak": "Iraq",
    "Israel": "Israel",
    "Jordanien": "Jordan",
    "Libanon": "Lebanon",
    "Saudi-Arabien": "Saudi Arabia",
    "Vereinigte Arabische Emirate": "United Arab Emirates",
    "Katar": "Qatar",
    "Kuwait": "Kuwait",

    "China": "China",
    "Japan": "Japan",
    "Südkorea": "South Korea",
    "Nordkorea": "North Korea",
    "Taiwan": "Taiwan",
    "Hongkong": "Hong Kong",

    "Thailand": "Thailand",
    "Vietnam": "Vietnam",
    "Malaysia": "Malaysia",
    "Singapur": "Singapore",
    "Indonesien": "Indonesia",
    "Philippinen": "Philippines",

    "Indien": "India",
    "Pakistan": "Pakistan",
    "Bangladesch": "Bangladesh",
    "Sri Lanka": "Sri Lanka",

    "Australien": "Australia",
    "Neuseeland": "New Zealand",

    "USA": "United States",
    "Vereinigte Staaten": "United States",
    "Kanada": "Canada",
    "Mexiko": "Mexico",

    "Brasilien": "Brazil",
    "Argentinien": "Argentina",
    "Chile": "Chile",
    "Uruguay": "Uruguay",
    "Paraguay": "Paraguay",
    "Bolivien": "Bolivia",
    "Peru": "Peru",
    "Kolumbien": "Colombia",
    "Venezuela": "Venezuela",
    "Ecuador": "Ecuador",

    "Costa Rica": "Costa Rica",
    "Panama": "Panama",
    "Guatemala": "Guatemala",
    "Honduras": "Honduras",
    "El Salvador": "El Salvador",
    "Nicaragua": "Nicaragua",

    "Marokko": "Morocco",
    "Algerien": "Algeria",
    "Tunesien": "Tunisia",
    "Libyen": "Libya",
    "Ägypten": "Egypt",

    "Nigeria": "Nigeria",
    "Ghana": "Ghana",
    "Elfenbeinküste": "Ivory Coast",
    "Senegal": "Senegal",
    "Mali": "Mali",
    "Kamerun": "Cameroon",
    "DR Kongo": "DR Congo",
    "Südafrika": "South Africa",
}

# ==========================================================
# PLAYER STATUS
# ==========================================================

STATUS_MAP = {
    "Vereinslos": "Without a club",
    "Karriereende": "Retired",
    "Unbekannt": "Unknown",
}

# ==========================================================
# FOOT
# ==========================================================

FOOT_MAP = {
    "rechts": "Right",
    "links": "Left",
    "beidfüßig": "Both",
}

# ==========================================================
# POSITIONS
# ==========================================================

POSITION_MAP = {
    "Torwart": "Goalkeeper",
    "Abwehr": "Defence",
    "Mittelfeld": "Midfield",
    "Sturm": "Attack",
}
