import requests
from bs4 import BeautifulSoup

url = "https://ma.indeed.com/jobs?q=Graphic+Designer&l=Morocco"

headers = {
"User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=30)

print("STATUS:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

titles = soup.select("h2.jobTitle")

print("OFFERS FOUND:", len(titles))

for title in titles[:10]:
print("-", title.get_text(" ", strip=True))
