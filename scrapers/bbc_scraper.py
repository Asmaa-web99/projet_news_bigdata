"""
Scraper pour BBC News (https://www.bbc.com/news)
Référence internationale anglophone.
"""
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from loguru import logger


class BBCScraper(BaseScraper):
    """Scraper pour BBC News."""

    def __init__(self):
        super().__init__(
            source_name="bbc",
            base_url="https://www.bbc.com/news",
            language="en",
            country="UK"
        )
        # Pattern URL article BBC : /news/articles/XXXX ou /news/world-XXXX
        self.article_pattern = re.compile(
            r'https://www\.bbc\.com/news/('
            r'articles/[a-z0-9]+'                                # /news/articles/c1d2e3...
            r'|[a-z]+-[a-z\-]*-?\d{6,}'                          # /news/world-europe-12345678
            r')$'
        )

    def get_article_links(self, max_articles: int = 10) -> list:
        """Récupère les URLs des derniers articles depuis la home page BBC News."""
        soup = self.fetch_page(self.base_url)
        if not soup:
            return []

        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            # BBC utilise des liens relatifs : /news/articles/...
            if href.startswith('/news/'):
                href = f"https://www.bbc.com{href}"
            
            if self.article_pattern.match(href):
                links.add(href)
                if len(links) >= max_articles:
                    break

        logger.info(f"  → {len(links)} URLs d'articles détectées")
        return list(links)[:max_articles]

    def parse_article(self, url: str) -> dict | None:
        """Extrait les informations d'un article BBC."""
        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            # Titre : <h1>
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "No title"

            # Auteur
            author = "BBC News"
            meta_author = soup.find('meta', {'name': 'author'})
            if meta_author:
                author = meta_author.get('content', 'BBC News')

            # Date : meta property
            date = ""
            meta_date = soup.find('meta', {'property': 'article:published_time'})
            if meta_date:
                date = meta_date.get('content', '')
            if not date:
                time_tag = soup.find('time')
                if time_tag:
                    date = time_tag.get('datetime', '')

            # Catégorie : essayer plusieurs sources dans l'ordre
            category = "News"

            # 1. Meta property article:section (plus fiable)
            meta_section = soup.find('meta', {'property': 'article:section'})
            if meta_section and meta_section.get('content'):
                category = meta_section.get('content').strip()
            else:
                # 2. Topical breadcrumb (BBC utilise data-component="tag")
                breadcrumb = soup.find('a', {'data-testid': 'topic-link'}) or \
                            soup.find('span', {'data-testid': 'topic-tag'})
                if breadcrumb:
                    category = breadcrumb.get_text(strip=True)
                else:
                    # 3. Fallback intelligent depuis l'URL
                    # Format: /news/world-europe-12345 ou /news/articles/abc123
                    url_path = url.replace('https://www.bbc.com/news/', '')
                    if url_path.startswith('articles/'):
                        # Pour les articles modernes, chercher dans le HTML un tag de topic
                        tag_link = soup.find('a', href=lambda h: h and '/news/topics/' in h)
                        if tag_link:
                            category = tag_link.get_text(strip=True)
                        else:
                            category = "World News"  # Fallback générique
                    else:
                        # Format: world-europe-12345 → World
                        first_part = url_path.split('-')[0]
                        category_map = {
                            'world': 'World',
                            'business': 'Business',
                            'technology': 'Technology',
                            'sport': 'Sport',
                            'health': 'Health',
                            'science': 'Science',
                            'politics': 'Politics',
                            'entertainment': 'Entertainment',
                        }
                        category = category_map.get(first_part, first_part.capitalize() if first_part else "News")

            # Contenu : article body
            content = ""
            # BBC utilise plusieurs structures : article > main > div[data-component]
            content_div = soup.find('article') or soup.find('main')
            
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
    scraper = BBCScraper()
    scraper.run(max_articles=20, delay=1.5)