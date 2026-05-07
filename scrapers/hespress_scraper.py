"""
Scraper pour Hespress (https://fr.hespress.com)
Site marocain francophone le plus visité.
"""
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from loguru import logger


class HespressScraper(BaseScraper):
    """Scraper pour Hespress (version française)."""

    def __init__(self):
        super().__init__(
            source_name="hespress",
            base_url="https://fr.hespress.com",
            language="fr",
            country="MA"
        )
        # Pattern URL article : domaine + ID numérique + titre + .html
        self.article_pattern = re.compile(
            r'https://fr\.hespress\.com/\d{5,7}-[\w\-]+\.html$'
        )

    def get_article_links(self, max_articles: int = 10) -> list:
        """Récupère les URLs des derniers articles depuis la home page."""
        soup = self.fetch_page(self.base_url)
        if not soup:
            return []

        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if self.article_pattern.match(href):
                links.add(href)
                if len(links) >= max_articles:
                    break

        logger.info(f"  → {len(links)} URLs d'articles détectées")
        return list(links)[:max_articles]

    def parse_article(self, url: str) -> dict | None:
        """Extrait les informations d'un article Hespress."""
        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            # Titre : <h1>
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "Sans titre"

            # Auteur : meta tag ou span auteur
            author = ""
            meta_author = soup.find('meta', {'name': 'author'})
            if meta_author:
                author = meta_author.get('content', '')
            if not author:
                author_tag = soup.find('span', class_='author') or \
                             soup.find('a', class_='author')
                if author_tag:
                    author = author_tag.get_text(strip=True)
            if not author:
                author = "Hespress"

            # Date de publication : meta property
            date = ""
            meta_date = soup.find('meta', {'property': 'article:published_time'})
            if meta_date:
                date = meta_date.get('content', '')
            if not date:
                time_tag = soup.find('time')
                if time_tag:
                    date = time_tag.get('datetime', '') or time_tag.get_text(strip=True)

            # Catégorie : meta section ou breadcrumb
            category = ""
            meta_section = soup.find('meta', {'property': 'article:section'})
            if meta_section:
                category = meta_section.get('content', '')
            if not category:
                category = "Général"

            # Contenu : div principal de l'article
            content = ""
            content_div = soup.find('div', class_='article-content') or \
                          soup.find('div', class_='post-content') or \
                          soup.find('div', {'itemprop': 'articleBody'})
            
            if content_div:
                paragraphs = content_div.find_all('p')
                content = "\n".join([
                    p.get_text(strip=True) 
                    for p in paragraphs 
                    if p.get_text(strip=True)
                ])
            
            # Fallback : prendre tous les <p> de la page si div introuvable
            if not content:
                all_p = soup.find_all('p')
                content = "\n".join([
                    p.get_text(strip=True) 
                    for p in all_p 
                    if len(p.get_text(strip=True)) > 50  # paragraphes substantiels
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


# ===== TEST DIRECT =====
if __name__ == "__main__":
    scraper = HespressScraper()
    scraper.run(max_articles=20, delay=1.5)