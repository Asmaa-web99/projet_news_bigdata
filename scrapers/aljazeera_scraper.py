"""
Scraper pour Al Jazeera English (https://www.aljazeera.com/news)
Référence du Monde Arabe en anglais.
"""
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from loguru import logger


class AlJazeeraScraper(BaseScraper):
    """Scraper pour Al Jazeera English."""

    def __init__(self):
        super().__init__(
            source_name="aljazeera",
            base_url="https://www.aljazeera.com/news/",
            language="en",
            country="QA"
        )
        # Pattern Al Jazeera : /section/YYYY/M/D/titre
        # On EXCLUT video et podcasts (pas vraiment des articles texte)
        self.article_pattern = re.compile(
            r'https://www\.aljazeera\.com/(news|sports|features|opinion|economy)/\d{4}/\d{1,2}/\d{1,2}/[\w\-]+$'
        )

    def get_article_links(self, max_articles: int = 10) -> list:
        """Récupère les URLs des derniers articles."""
        soup = self.fetch_page(self.base_url)
        if not soup:
            return []

        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Convertir liens relatifs en absolus
            if href.startswith('/'):
                href = f"https://www.aljazeera.com{href}"
            
            if self.article_pattern.match(href):
                links.add(href)
                if len(links) >= max_articles:
                    break

        logger.info(f"  → {len(links)} URLs d'articles détectées")
        return list(links)[:max_articles]

    def parse_article(self, url: str) -> dict | None:
        """Extrait les informations d'un article Al Jazeera."""
        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            # Titre
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "No title"

            # Auteur
            author = "Al Jazeera"
            meta_author = soup.find('meta', {'name': 'author'})
            if meta_author:
                author = meta_author.get('content', 'Al Jazeera')
            else:
                # Al Jazeera utilise parfois <a class="author-link">
                author_tag = soup.find('a', class_='author-link') or \
                             soup.find('span', class_='article-author-name')
                if author_tag:
                    author = author_tag.get_text(strip=True)

            # Date
            date = ""
            meta_date = soup.find('meta', {'property': 'article:published_time'})
            if meta_date:
                date = meta_date.get('content', '')

            # Catégorie : extraite de l'URL
            category = "News"
            url_parts = url.replace('https://www.aljazeera.com/', '').split('/')
            if url_parts:
                category = url_parts[0].capitalize()

            # Contenu : Al Jazeera utilise <main> avec <p>
            content = ""
            content_div = soup.find('main') or \
                          soup.find('div', class_='wysiwyg') or \
                          soup.find('article')
            
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
    scraper = AlJazeeraScraper()
    scraper.run(max_articles=20, delay=1.5)