import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "https://www.akhbarona.com/"
response = requests.get(url, headers=headers, timeout=15)
print(f"Status: {response.status_code}")
print(f"Encoding: {response.encoding}")

soup = BeautifulSoup(response.text, 'lxml')

# Échantillon de liens
print("\n🔍 Échantillon de liens (20 premiers articles potentiels) :")
seen = set()
for a in soup.find_all('a', href=True):
    href = a['href']
    if 'akhbarona.com' in href and href not in seen:
        seen.add(href)
        print(f"  → {href}")
        if len(seen) >= 20:
            break