import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

sites_to_test = {
    "20 Minutes": "https://www.20minutes.fr/",
    "TV5 Monde": "https://information.tv5monde.com/",
    "Ouest France": "https://www.ouest-france.fr/",
    "France Info": "https://www.francetvinfo.fr/",
    "Le Figaro": "https://www.lefigaro.fr/",
    "RFI": "https://www.rfi.fr/fr/",
}

print("🔍 Test des sites francophones disponibles :\n")
for name, url in sites_to_test.items():
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        nb_links = len(soup.find_all('a', href=True))
        status_emoji = "✅" if r.status_code == 200 else "❌"
        print(f"{status_emoji} {name:15} | Status: {r.status_code} | HTML: {len(r.text):>8} chars | Links: {nb_links}")
    except Exception as e:
        print(f"❌ {name:15} | ERREUR : {str(e)[:50]}")