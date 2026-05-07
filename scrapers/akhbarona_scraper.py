"""
Scraper pour Akhbarona (https://www.akhbarona.com)
Site marocain arabophone très populaire.
"""
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from loguru import logger


class AkhbaronaScraper(BaseScraper):
    """Scraper pour Akhbarona (arabe)."""

    def __init__(self):
        super().__init__(
            source_name="akhbarona",
            base_url="https://www.akhbarona.com",
            language="ar",
            country="MA"
        )
        # Pattern : /catégorie/ID-numérique.html (et PAS index.X.html)
        self.article_pattern = re.compile(
            r'https://www\.akhbarona\.com/[a-z]+/\d{5,8}\.html$'
        )

    def get_article_links(self, max_articles: int = 10) -> list:
        """Récupère les URLs des derniers articles depuis la home page."""
        soup = self.fetch_page(self.base_url)
        if not soup:
            return []

        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Exclure les pages de catégorie (contiennent 'index.')
            if 'index.' in href:
                continue
            if self.article_pattern.match(href):
                links.add(href)
                if len(links) >= max_articles:
                    break

        logger.info(f"  → {len(links)} URLs d'articles détectées")
        return list(links)[:max_articles]

    def parse_article(self, url: str) -> dict | None:
        """Extrait les informations d'un article Akhbarona."""
        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            # Titre : <h1>
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "بدون عنوان"

            # Auteur
            author = "Akhbarona"
            meta_author = soup.find('meta', {'name': 'author'})
            if meta_author:
                author = meta_author.get('content', 'Akhbarona')

            # Date
            date = ""
            meta_date = soup.find('meta', {'property': 'article:published_time'})
            if meta_date:
                date = meta_date.get('content', '')

            # Catégorie : extraite de l'URL (akhbarona.com/economy/123.html → economy)
            category = "أخبار"  # "actualités" en arabe par défaut
            url_parts = url.replace('https://www.akhbarona.com/', '').split('/')
            if url_parts and url_parts[0] not in ('', 'index'):
                category = url_parts[0]

            # Contenu : div principal
            content = ""
            content_div = soup.find('div', {'id': 'article_body'}) or \
                          soup.find('div', class_='article_body') or \
                          soup.find('article')
            
            if content_div:
                paragraphs = content_div.find_all('p')
                content = "\n".join([
                    p.get_text(strip=True) 
                    for p in paragraphs 
                    if p.get_text(strip=True)
                ])
            
            # Fallback
            if not content:
                all_p = soup.find_all('p')
                content = "\n".join([
                    p.get_text(strip=True) 
                    for p in all_p 
                    if len(p.get_text(strip=True)) > 50
                ])

            return {
                'url': url,
                'title': title,
                'author': author,
                'publication_date': date,
                'category': category,
                'content': content,
                'word_count': len(content.split()) if content else 0,
            }

        except Exception as e:
            logger.error(f"Erreur parsing {url}: {e}")
            return None


if __name__ == "__main__":
    scraper = AkhbaronaScraper()
    scraper.run(max_articles=20, delay=1.5)