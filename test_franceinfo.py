import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "https://www.francetvinfo.fr/"
response = requests.get(url, headers=headers, timeout=15)
print(f"Status: {response.status_code}")
print(f"Taille HTML: {len(response.text)} caractères\n")

soup = BeautifulSoup(response.text, 'lxml')

print("🔍 Échantillon de 20 liens :")
seen = set()
for a in soup.find_all('a', href=True):
    href = a['href']
    if href.startswith('/'):
        href = f"https://www.francetvinfo.fr{href}"
    
    if 'francetvinfo.fr' in href and href not in seen and not href.endswith('.fr/') and not href.endswith('.fr'):
        seen.add(href)
        print(f"  → {href}")
        if len(seen) >= 20:
            break