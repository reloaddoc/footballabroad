import re
import time
import random
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

INPUT = "players.csv"
OUTPUT = "output/player_profiles.csv"

HEADLESS = True


def clean(t):
    return None if t is None else " ".join(t.split()).strip()


def extract_player_id(v):
    v = str(v)
    m = re.search(r"/spieler/(\d+)", v)
    return m.group(1) if m else (v if v.isdigit() else None)


def find_info_table(soup):
    for d in soup.find_all("div", class_="info-table"):
        if "Geb./Alter" in d.get_text(" ", strip=True):
            return d
    return None


def parse_info_table(info):
    out = {}
    if info is None:
        return out

    labels = info.find_all(
        "span",
        class_=lambda c: c and "info-table__content--regular" in c
    )

    for lab in labels:
        key = clean(lab.get_text()).rstrip(":")
        val = lab.find_next_sibling("span")

        if not val:
            continue

        texts = []
        hrefs = []

        # ---------- Nationality ----------
        if key in ("Staatsbürgerschaft", "Nationalität"):

            flags = []

            # 1. Flaggen
            for img in val.find_all("img"):

                title = clean(img.get("title"))

                if title:
                    flags.append(title)

            # 2. Links
            if not flags:

                for a in val.find_all("a"):

                    txt = clean(a.get_text())

                    if txt:
                        flags.append(txt)

            # 3. LETZTER FALLBACK
            if not flags:

                txt = clean(val.get_text(" ", strip=True))

                if txt:
                    flags.append(txt)

            texts = list(dict.fromkeys(flags))

            for a in val.find_all("a"):

                href = a.get("href")

                if href:
                    hrefs.append(href)

            out[key] = ";".join(texts)

            out[key + "_link"] = (
                ";".join(dict.fromkeys(hrefs))
                if hrefs
                else None
            )

        # ---------- Everything else ----------
        else:
            for a in val.find_all("a"):
                txt = clean(a.get_text()) or clean(a.get("title"))
                if txt:
                    texts.append(txt)

                href = a.get("href")
                if href:
                    hrefs.append(href)

            out[key] = (
                " | ".join(dict.fromkeys(texts))
                if texts
                else clean(val.get_text(" ", strip=True))
            )

            out[key + "_link"] = (
                " | ".join(dict.fromkeys(hrefs))
                if hrefs
                else None
            )

    return out


Path("output").mkdir(exist_ok=True)
players = pd.read_csv(INPUT, encoding="utf-8-sig")

# ----------------------------------------------------
# Resume (FEHLER HIER BEHOBEN)
# ----------------------------------------------------
if Path(OUTPUT).exists():
    existing = pd.read_csv(OUTPUT, encoding="utf-8-sig")
    rows = existing.to_dict("records")

    existing = existing[
        ~existing["full_name"].fillna("").str.contains(
            "Bad Gateway|Gateway Time-out|Gateway Timeout",
            case=False,
            regex=True
        )
    ]
    rows = existing.to_dict("records")
    done = set(existing["player_id"].astype(str))
    print(f"{len(done)} Spieler bereits vorhanden.")
else:
    rows = []
    done = set()

# ----------------------------------------------------

with sync_playwright() as p:
    browser = p.chromium.launch(headless=HEADLESS)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/137.0 Safari/537.36",
        viewport={"width": 1600, "height": 1200}
    )

    page.set_default_timeout(90000)
    page.set_default_navigation_timeout(90000)

    total = len(players)
    scraped = len(done)

    # HAUPTSCHLEIFE STARTET HIER
    for raw in players.iloc[:, 0]:
        pid = extract_player_id(raw)

        if not pid:
            continue

        if pid in done:
            continue

        scraped += 1
        print(f"[{scraped}/{total}] {pid}")

        # Browser regelmäßig neu starten
        if scraped % 100 == 0:
            page.close()
            browser.close()
            browser = p.chromium.launch(headless=HEADLESS)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/137.0 Safari/537.36",
                viewport={"width": 1600, "height": 1200}
            )
            page.set_default_timeout(90000)
            page.set_default_navigation_timeout(90000)
            print("Browser neu gestartet.")

        success = False
        for attempt in range(3):
            try:
                page.goto(
                    f"https://www.transfermarkt.de/-/profil/spieler/{pid}",
                    wait_until="domcontentloaded",
                    timeout=90000
                )
                success = True
                break
            except Exception as e:
                print(f"Retry {attempt+1}/3 ({pid})")
                time.sleep(5)

        # FEHLER HIER BEHOBEN: Bleibt in der Schleife eingerückt
        if not success:
            print(f"Übersprungen: {pid}")
            continue

        # HTML holen
        html = page.content()

        # Gateway-Fehler erkennen
        if (
            "502 Bad Gateway" in html
            or "504 Gateway Time-out" in html
            or "Gateway Timeout" in html
        ):
            print(f"Gateway Error ({pid}) -> Browser wird neu gestartet")
            page.close()
            browser.close()

            browser = p.chromium.launch(headless=HEADLESS)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/137.0 Safari/537.36",
                viewport={"width": 1600, "height": 1200}
            )
            page.set_default_timeout(90000)
            page.set_default_navigation_timeout(90000)
            time.sleep(5)
            continue

        # BeautifulSoup & Parsing (FEHLER HIER BEHOBEN: Eingerückt)
        soup = BeautifulSoup(html, "html.parser")
        d = parse_info_table(find_info_table(soup))

        full_name = d.get("Name im Heimatland")
        if not full_name:
            if soup.title:
                full_name = clean(soup.title.get_text()).split(
                    " - Spielerprofil")[0]
            else:
                full_name = "Unbekannter Spieler"

        # Zeile hinzufügen
        # vorhandenen Datensatz desselben Spielers entfernen
        rows = [
            r for r in rows
            if str(r["player_id"]) != str(pid)
        ]

        rows.append({
            "player_id": pid,
            "full_name": full_name,
            "date_of_birth": d.get("Geb./Alter"),
            "place_of_birth": d.get("Geburtsort"),
            "height": d.get("Größe"),
            "position": d.get("Position"),
            "foot": d.get("Fuß"),
            "nationality": d.get("Staatsbürgerschaft") or d.get("Nationalität"),
            "nationality_link": d.get("Staatsbürgerschaft_link") or d.get("Nationalität_link"),
            "agent": d.get("Spielerberater") or d.get("Berater"),
            "agent_link": d.get("Spielerberater_link") or d.get("Berater_link"),
            "current_club": d.get("Aktueller Verein"),
            "current_club_link": d.get("Aktueller Verein_link"),
            "contract_until": d.get("Vertrag bis"),
            "joined": d.get("Im Verein seit")
        })

        done.add(pid)

        # Teilschritt speichern
        pd.DataFrame(rows).to_csv(
            OUTPUT,
            index=False,
            encoding="utf-8-sig"
        )

        time.sleep(random.uniform(1.2, 2.5))

    # Browser wird nach Ende der Hauptschleife sauber geschlossen
    browser.close()

print()
print("=" * 60)
print("FERTIG")
print("=" * 60)
print(f"Spieler gespeichert: {len(rows)}")
print(f"Datei: {OUTPUT}")
