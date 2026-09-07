import os
import json
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urljoin, quote

BASE_URL = "https://ma.indeed.com"
STATE_FILE = "seen.json"

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TO_EMAIL = "[yassirsoundpeats@gmail.com](mailto:yassirsoundpeats@gmail.com)"

SEARCHES = [
"Graphic Designer",
"Motion Designer",
"Art Director",
"Creative Director",
"Graphic Motion Designer",
"Infographiste",
"Creative Designer",
"3D Designer",
]

MAX_PAGES = 5

def load_seen():
if not os.path.exists(STATE_FILE):
return set()

```
try:
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("seen", []))
except Exception:
    return set()
```

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
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36"
})

```
offers = {}

for search in SEARCHES:
    for page in range(MAX_PAGES):
        start = page * 10

        url = (
            f"{BASE_URL}/jobs?"
            f"q={quote(search)}"
            f"&l=Morocco"
            f"&start={start}"
        )

        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"Erreur Indeed ({search}, page {page + 1}): {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        cards = soup.select("div.job_seen_beacon")

        if not cards:
            cards = soup.select("div.cardOutline")

        found = 0

        for card in cards:
            link = card.select_one("a[href*='/viewjob']")

            title_el = card.select_one(
                "h2.jobTitle a, h2.jobTitle span"
            )

            if not link:
                continue

            title = (
                title_el.get_text(" ", strip=True)
                if title_el
                else link.get_text(" ", strip=True)
            )

            href = link.get("href", "").strip()

            if not title or not href:
                continue

            full_url = urljoin(BASE_URL, href)

            offers[full_url] = {
                "title": title,
                "url": full_url,
                "search": search,
            }

            found += 1

        print(f"{search} | page {page + 1} | {found} offres")

        if found == 0:
            break

return list(offers.values())
```

def send_email(new_offers):
if not new_offers:
return

```
msg = MIMEMultipart("alternative")
msg["From"] = GMAIL_ADDRESS
msg["To"] = TO_EMAIL
msg["Subject"] = f"{len(new_offers)} nouvelle(s) offre(s) Designer"

html = """
<html>
<body>
    <h2>Nouvelles offres Designer</h2>
    <p>Nouvelles offres détectées sur Indeed Maroc :</p>
    <ul>
"""

for offer in new_offers:
    html += f"""
    <li>
        <strong>{offer['title']}</strong><br>
        Recherche : {offer['search']}<br>
        <a href="{offer['url']}">Voir l'offre sur Indeed</a>
    </li>
    <br>
    """

html += """
    </ul>
    <p>Source : Indeed Maroc</p>
</body>
</html>
"""

msg.attach(MIMEText(html, "html", "utf-8"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
    server.sendmail(
        GMAIL_ADDRESS,
        TO_EMAIL,
        msg.as_string()
    )

print("Email envoyé avec succès.")
```

def main():
print("Recherche des offres Designer sur Indeed Maroc...")

```
seen = load_seen()
offers = get_offers()

print(f"Total offres trouvées : {len(offers)}")

current_ids = {offer["url"] for offer in offers}

if not seen:
    save_seen(current_ids)
    print("Première تشغيل : baseline créée.")
    return

new_offers = [
    offer
    for offer in offers
    if offer["url"] not in seen
]

if new_offers:
    print(f"Nouvelles offres : {len(new_offers)}")
    send_email(new_offers)
else:
    print("Aucune nouvelle offre.")

save_seen(seen | current_ids)
```

if **name** == "**main**":
main()
