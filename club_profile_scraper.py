import re
import time
import random
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


# =====================================================
# Einstellungen
# =====================================================

INPUT = "output/clubs.csv"
OUTPUT = "output/club_profiles.csv"

HEADLESS = True

# =====================================================
# Hilfsfunktionen
# =====================================================


def clean(text):
    if text is None:
        return None
    return " ".join(text.split()).strip()


def extract_club_id(value):
    value = str(value)
    m = re.search(r"/verein/(\d+)", value)
    if m:
        return m.group(1)
    if value.isdigit():
        return value
    return None


# =====================================================
# Daten laden
# =====================================================

clubs = pd.read_csv(INPUT, encoding="utf-8-sig")
clubs["club_id"] = clubs["club_id"].astype(str)

Path("output").mkdir(exist_ok=True)

# =====================================================
# Resume
# =====================================================

if Path(OUTPUT).exists():
    existing = pd.read_csv(OUTPUT, encoding="utf-8-sig")
    rows = existing.to_dict("records")
    done = set(existing["club_id"].astype(str))
    print(f"{len(done)} Vereine bereits vorhanden.")
else:
    rows = []
    done = set()

# =====================================================
# Browser
# =====================================================

with sync_playwright() as p:
    browser = p.chromium.launch(headless=HEADLESS)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/137.0 Safari/537.36",
        viewport={"width": 1600, "height": 1200},
    )

    page.set_default_timeout(90000)
    page.set_default_navigation_timeout(90000)

    total = len(clubs)
    counter = 0

    # `.head(10)` extrahiert testweise nur die ersten 10 Zeilen
    for _, club in clubs.iterrows():
        club_id = str(club["club_id"])
        slug = club.get("slug")

        if pd.isna(slug):
            continue

        if club_id in done:
            continue

        counter += 1
        print(f"[{counter}/{total}] {club_id}")

        url = f"https://www.transfermarkt.de/{slug}/startseite/verein/{club_id}"
        success = False

        for attempt in range(3):
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=90000)
                success = True
                break
            except Exception:
                print(f"Retry {attempt+1}/3")
                time.sleep(5)

        if not success:
            print("Übersprungen")
            continue

        soup = BeautifulSoup(page.content(), "html.parser")
        header = soup.select_one(".data-header")

        # -------------------------------------------------
        # Hilfsfunktionen innerhalb der Schleife
        # -------------------------------------------------

        def value_after_label(label):
            spans = soup.find_all("span")
            for span in spans:
                txt = clean(span.get_text())
                if txt is None:
                    continue
                if txt.startswith(label):
                    nxt = span.find_next_sibling()
                    if nxt:
                        return clean(nxt.get_text(" ", strip=True))
            return None

        def link_after_label(label):
            spans = soup.find_all("span")
            for span in spans:
                txt = clean(span.get_text())
                if txt is None:
                    continue
                if txt.startswith(label):
                    nxt = span.find_next_sibling()
                    if nxt:
                        a = nxt.find("a")
                        if a:
                            return (clean(a.get_text()), a.get("href"))
            return (None, None)

        # -------------------------------------------------
        # schema.org Daten extrahieren
        # -------------------------------------------------

        official = None
        x = soup.find(attrs={"itemprop": "legalName"})
        if x:
            official = clean(x.get_text())

        city = None
        x = soup.find(attrs={"itemprop": "postalCode"})
        if x:
            city = clean(x.get_text())

        country = None
        x = soup.find(attrs={"itemprop": "addressLocality"})
        if x:
            country = clean(x.get_text())

        founded = None
        x = soup.find(attrs={"itemprop": "foundingDate"})
        if x:
            founded = clean(x.get_text())

        # -------------------------------------------------
        # -------------------------------------------------
        # Liga
        # -------------------------------------------------

        league_name = None
        league_link = None
        league_country = None
        league_level = None
        league_code = None

        affiliation = soup.find("span", attrs={"itemprop": "affiliation"})

        if affiliation:

            a = affiliation.find("a")

            if a:

                league_name = clean(a.get_text())
                league_link = a.get("href")

                if league_link:

                    m = re.search(r"/wettbewerb/([A-Za-z0-9]+)", league_link)

                    if m:
                        league_code = m.group(1)

        # Ligahöhe + Land

        for label in soup.select("span.data-header__label"):

            strong = label.find("strong")

            if strong and "Ligahöhe" in strong.get_text():

                content = label.find("span", class_="data-header__content")

                if content:

                    flag = content.find("img")

                    if flag:

                        league_country = flag.get("title")

                    text = clean(content.get_text(" ", strip=True))

                    if text:

                        text = text.replace(league_country or "", "").strip()

                        league_level = text

        # -------------------------------------------------
        # Weitere Daten extrahieren
        # -------------------------------------------------

        coach_name, coach_link = link_after_label("Trainer:")
        stadium = value_after_label("Stadion:")
        capacity = value_after_label("Plätze:")
        website = value_after_label("Homepage:")
        colors = value_after_label("Vereinsfarben:")

        # Zeile hinzufügen
        rows.append(
            {
                "club_id": club_id,
                "slug": slug,
                "name": club.get("name"),
                "official_name": official,
                "city": city,
                "country": country,
                "founded": founded,
                "league": league_name,
                "league_link": league_link,
                "league_country": league_country,
                "league_level": league_level,
                "league_code": league_code,
                "coach": coach_name,
                "coach_link": coach_link,
                "stadium": stadium,
                "capacity": capacity,
                "website": website,
                "colors": colors,
            }
        )

        done.add(club_id)

        # In jedem Durchlauf als Backup speichern
        pd.DataFrame(rows).to_csv(OUTPUT, index=False, encoding="utf-8-sig")

        # Höfliche Pause einlegen
        time.sleep(random.uniform(1.0, 2.0))

    # Browser nach Ende der Schleife schließen (noch im "with"-Block)
    browser.close()

# =====================================================
# Finale Aufbereitung & Speichern
# =====================================================

if rows:
    df = pd.DataFrame(rows)

    # Doppelte Clubs entfernen
    df = df.drop_duplicates(subset=["club_id"])

    # Nach Vereinsname sortieren
    df = df.sort_values(by="name", na_position="last")

    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

    print()
    print("=" * 70)
    print("CLUB PROFILE SCRAPER")
    print("=" * 70)
    print(f"Vereine gespeichert : {len(df):,}")
    print()
    print("Vorschau:")
    # Sicherstellen, dass die Spalten existieren, bevor sie geprintet werden
    cols_to_print = [c for c in ["name", "country",
                                 "league", "coach"] if c in df.columns]
    print(df[cols_to_print].head(15))
    print()
    print("Datei gespeichert:")
    print(OUTPUT)
    print("=" * 70)
else:
    print("Keine neuen Daten gescrapet.")
