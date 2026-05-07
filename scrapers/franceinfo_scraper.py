"""
Scraper pour France Info (https://www.francetvinfo.fr)
Service public français d'information - gratuit, sans paywall.
"""
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from loguru import logger


class FranceInfoScraper(BaseScraper):
    """Scraper pour France Info."""

    def __init__(self):
        super().__init__(
            source_name="franceinfo",
            base_url="https://www.francetvinfo.fr",
            language="fr",
            country="FR"
        )
        # Pattern : URL doit finir par _NUMERO.html
        self.article_pattern = re.compile(
            r'https://www\.francetvinfo\.fr/[\w\-/]+_\d{6,8}\.html$'
        )

    def get_article_links(self, max_articles: int = 10) -> list:
        """Récupère les URLs des derniers articles."""
        soup = self.fetch_page(self.base_url)
        if not soup:
            return []

        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                href = f"https://www.francetvinfo.fr{href}"
            
            if self.article_pattern.match(href):
                links.add(href)
                if len(links) >= max_articles:
                    break

        logger.info(f"  → {len(links)} URLs d'articles détectées")
        return list(links)[:max_articles]

    def parse_article(self, url: str) -> dict | None:
        """Extrait les informations d'un article France Info."""
        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            # Titre
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "Sans titre"

            # Auteur
            author = "France Info"
            meta_author = soup.find('meta', {'name': 'author'})
            if meta_author:
                author = meta_author.get('content', 'France Info')
            else:
                author_tag = soup.find('span', class_='author') or \
                             soup.find('div', class_='author')
                if author_tag:
                    author = author_tag.get_text(strip=True)

            # Date
            date = ""
            meta_date = soup.find('meta', {'property': 'article:published_time'})
            if meta_date:
                date = meta_date.get('content', '')

            # Catégorie : extraite de l'URL
            # Ex: francetvinfo.fr/monde/iran/guerre.../direct-... → "monde"
            category = "Général"
            url_path = url.replace('https://www.francetvinfo.fr/', '').split('/')
            if url_path and url_path[0]:
                category = url_path[0].capitalize()

            # Contenu : France Info utilise différentes structures
            content = ""
            content_div = soup.find('div', class_='c-body') or \
                          soup.find('article') or \
                          soup.find('div', class_='content-article') or \
                          soup.find('main')
            
            if content_div:
                paragraphs = content_div.find_all('p')
                content = "\n".join([
                    p.get_text(strip=True) 
                    for p in paragraphs 
                    if p.get_text(strip=True) and len(p.get_text(strip=True)) > 30
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
    scraper = FranceInfoScraper()
    scraper.run(max_articles=20, delay=1.5)