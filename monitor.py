import os
import json
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urljoin

BASE_URL = "https://www.emploi-public.ma"
LIST_URL = f"{BASE_URL}/fr/concours-liste"

STATE_FILE = "seen.json"
MAX_PAGES = 10

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TO_EMAIL = "yassirsoundpeats@gmail.com"


def load_seen():
    if not os.path.exists(STATE_FILE):
        return set()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("seen", []))
    except Exception:
        return set()


def save_seen(seen):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"seen": sorted(seen)},
            f,
            ensure_ascii=False,
            indent=2
        )


def get_offers():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 Concours Monitor"
    })

    offers = []

    for page in range(1, MAX_PAGES + 1):
        url = LIST_URL if page == 1 else f"{LIST_URL}?page={page}"

        response = session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        found_on_page = 0

        for link in soup.find_all("a", href=True):
            href = link.get("href", "").strip()
            title = link.get_text(" ", strip=True)

            if not title or len(title) < 10:
                continue

            if "concours" not in href.lower() and "avis" not in href.lower():
                continue

            full_url = urljoin(BASE_URL, href)

            if full_url in [x["url"] for x in offers]:
                continue

            offers.append({
                "title": title,
                "url": full_url
            })

            found_on_page += 1

        if found_on_page == 0:
            break

    return offers


def send_email(new_offers):
    if not new_offers:
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg["Subject"] = f"🔔 Nouveau(x) concours au Maroc : {len(new_offers)}"

    html = """
    <html>
    <body>
    <h2>🔔 Nouveaux concours / recrutements</h2>
    <p>De nouvelles offres ont été détectées sur emploi-public.ma :</p>
    <ul>
    """

    for offer in new_offers:
        html += f"""
        <li>
            <strong>{offer['title']}</strong><br>
            <a href="{offer['url']}">Voir l'offre</a>
        </li>
        <br>
        """

    html += """
    </ul>
    <p>
        Source officielle :
        <a href="https://www.emploi-public.ma/">
        emploi-public.ma
        </a>
    </p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, TO_EMAIL, msg.as_string())


def main():
    print("🔎 Recherche des nouveaux concours...")

    seen = load_seen()
    offers = get_offers()

    print(f"📋 Offres trouvées : {len(offers)}")

    current_ids = {offer["url"] for offer in offers}

    # Première تشغيل: créer une baseline sans envoyer des centaines d'emails
    if not seen:
        save_seen(current_ids)
        print("✅ Première تشغيل terminée. Baseline créée.")
        return

    new_offers = [
        offer for offer in offers
        if offer["url"] not in seen
    ]

    if new_offers:
        print(f"🆕 Nouveaux concours : {len(new_offers)}")
        send_email(new_offers)
    else:
        print("ℹ️ Aucun nouveau concours.")

    save_seen(seen | current_ids)


if __name__ == "__main__":
    main()
