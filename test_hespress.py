import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "https://fr.hespress.com"
response = requests.get(url, headers=headers, timeout=15)
print(f"Status: {response.status_code}")
print(f"Taille HTML: {len(response.text)} caractères")

soup = BeautifulSoup(response.text, 'lxml')

# Compter tous les liens
all_links = soup.find_all('a', href=True)
print(f"\nTotal de liens sur la page: {len(all_links)}")

# Afficher les 20 premiers liens uniques contenant "hespress"
print("\n🔍 Échantillon de liens hespress (20 premiers) :")
seen = set()
for a in all_links:
    href = a['href']
    if 'hespress' in href and href not in seen:
        seen.add(href)
        print(f"  → {href}")
        if len(seen) >= 20:
            break

# Chercher les balises <article>
articles = soup.find_all('article')
print(f"\n📰 Nombre de balises <article>: {len(articles)}")

# Chercher des classes typiques d'articles
for cls in ['post', 'article-card', 'card-article', 'news-item', 'article-item']:
    items = soup.find_all(class_=cls)
    if items:
        print(f"   Classe '{cls}': {len(items)} éléments trouvés")