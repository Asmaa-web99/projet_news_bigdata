import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "https://www.aljazeera.com/news/"
response = requests.get(url, headers=headers, timeout=15)
print(f"Status: {response.status_code}")
print(f"Taille HTML: {len(response.text)} caractères")

soup = BeautifulSoup(response.text, 'lxml')

# Total des liens
all_links = soup.find_all('a', href=True)
print(f"Total de liens : {len(all_links)}\n")

# Pattern d'articles : URLs avec date /YYYY/MM/DD/
article_pattern = re.compile(r'/\d{4}/\d{1,2}/\d{1,2}/')

print("🔍 Liens avec dates (vrais articles) :")
seen = set()
for a in all_links:
    href = a['href']
    if href.startswith('/'):
        href = f"https://www.aljazeera.com{href}"
    
    if article_pattern.search(href) and href not in seen:
        seen.add(href)
        print(f"  → {href}")
        if len(seen) >= 15:
            break

print(f"\nTotal articles détectés : {len(seen)}")

# Aussi chercher des balises article ou h3 avec liens
print("\n🔍 Structure HTML des articles (5 premiers <article>) :")
articles = soup.find_all('article')
print(f"Nombre de balises <article>: {len(articles)}")