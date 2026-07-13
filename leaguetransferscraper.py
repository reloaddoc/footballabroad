import csv
import os
import time
import requests
from bs4 import BeautifulSoup

INPUT_CSV_URLS = "leaguetransferurls.csv"
OUTPUT_CSV_RESULTS = os.path.join("output", "auslandstransfers.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


def scrape_single_url(url, heimatland, existing_player_urls):
    """Scraped eine Transfermarkt-URL mit aggressivem Retry-Schutz."""
    print(f"Scrape: {url}")
    print(f"-> Manuell gesetztes Heimatland für diese URL: '{heimatland}'")

    session = requests.Session()
    response = None

    # Exponential Backoff Retry-Logik (4 Versuche bei Fehlern/Timeouts)
    wait_times = [10, 20, 40, 60]
    for attempt, wait_time in enumerate(wait_times):
        try:
            response = session.get(url, headers=HEADERS, timeout=20)

            if response.status_code in [200, 404]:
                break

            print(
                f"Server meldet Status {response.status_code}. Blockade vermutet. Warte {wait_time} Sek..."
            )
            time.sleep(wait_time)

        except (
            requests.exceptions.RequestException,
            requests.exceptions.Timeout,
        ) as e:
            print(
                f"Verbindungsfehler/Timeout (Versuch {attempt + 1}/{len(wait_times)}): {e}"
            )
            print(f"Warte {wait_time} Sekunden vor dem nächsten Versuch...")
            time.sleep(wait_time)

    if not response or response.status_code != 200:
        print(f"❌ Seite endgültig fehlgeschlagen (Timeout/Block).")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("tr")
    found_urls = []

    for row in rows:
        player_div = row.find("div", class_="di nowrap")
        if not player_div:
            continue

        player_a = player_div.find("a")
        if not player_a or "profil/spieler" not in player_a.get("href", ""):
            continue

        player_href = player_a.get("href")
        player_url = f"https://www.transfermarkt.de{player_href}"

        if player_url in found_urls or player_url in existing_player_urls:
            continue

        verein_flagge_cell = row.find(
            "td", class_="verein-flagge-transfer-cell")
        is_ausland = False

        if verein_flagge_cell:
            flag_img = verein_flagge_cell.find("img", class_="flaggenrahmen")
            if flag_img:
                country_name = flag_img.get("alt", "").strip()
                country_title = flag_img.get("title", "").strip()

                # Nutzt jetzt den sauberen Wert direkt aus deiner CSV-Spalte
                if (
                    country_name
                    and country_name != heimatland
                    and country_title != heimatland
                ):
                    is_ausland = True

        if is_ausland:
            found_urls.append(player_url)

    return found_urls


def main():
    output_dir = os.path.dirname(OUTPUT_CSV_RESULTS)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    existing_player_urls = set()
    file_exists = os.path.exists(OUTPUT_CSV_RESULTS)

    if file_exists:
        try:
            with open(
                OUTPUT_CSV_RESULTS, mode="r", encoding="utf-8-sig"
            ) as file:
                for line in file:
                    clean_line = line.strip()
                    if clean_line:
                        existing_player_urls.add(clean_line)
            print(
                f"Resume-Logik aktiv: {len(existing_player_urls)} Spieler-URLs geladen."
            )
        except Exception as e:
            file_exists = False

# Ziel-URLs und die dazugehörigen Länder aus der CSV einlesen
    ligen_daten = []
    try:
        # utf-8-sig entfernt unsichtbare Excel-BOM-Zeichen am Dateianfang
        with open(INPUT_CSV_URLS, mode="r", encoding="utf-8-sig") as file:
            sample = file.read(2048)
            file.seek(0)

            # Erkennt automatisch, ob Komma oder Semikolon genutzt wird
            delimiter = ";" if ";" in sample else ","
            reader = csv.DictReader(file, delimiter=delimiter)

            for row in reader:
                # Macht den Spaltenabgleich unabhängig von Groß-/Kleinschreibung
                # Sucht nach url, URL, land, Land, LAND etc.
                url_val = None
                land_val = None

                for k, v in row.items():
                    if k and k.strip().lower() == "url":
                        url_val = v
                    if k and k.strip().lower() == "land":
                        land_val = v

                if url_val and land_val:
                    ligen_daten.append(
                        {"url": url_val.strip(), "land": land_val.strip()}
                    )
    except FileNotFoundError:
        print(f"Fehler: Datei '{INPUT_CSV_URLS}' fehlt.")
        return

    print(f"Gesamt-Pool: {len(ligen_daten)} Ligen-URLs in CSV gefunden.")
    mode = "w" if not file_exists else "a"

    with open(
        OUTPUT_CSV_RESULTS, mode=mode, newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        for idx, liga in enumerate(ligen_daten, 1):
            print(f"\n[{idx}/{len(ligen_daten)}]")
            new_player_urls = scrape_single_url(
                url=liga["url"],
                heimatland=liga["land"],
                existing_player_urls=existing_player_urls,
            )

            if new_player_urls:
                for p_url in new_player_urls:
                    writer.writerow([p_url])
                    existing_player_urls.add(p_url)
                file.flush()

            print(
                f"-> {len(new_player_urls)} neue echte Auslandstransfers gesichert."
            )

            time.sleep(5.0)

    print(f"\nFertig! Die bereinigten URLs liegen in '{OUTPUT_CSV_RESULTS}'.")


if __name__ == "__main__":
    main()
