import requests

url = "https://ma.indeed.com/jobs?q=Graphic+Designer&l=Morocco"

response = requests.get(
url,
headers={"User-Agent": "Mozilla/5.0"},
timeout=30
)

print("STATUS:", response.status_code)
print("PAGE LENGTH:", len(response.text))
print(response.text[:500])
