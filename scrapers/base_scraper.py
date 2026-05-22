"""
Classe parente pour tous les scrapers - VERSION PRO.
Améliorations : retry réseau, déduplication, logs persistés.
"""
import json
import time
import hashlib
from datetime import datetime
from io import BytesIO
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from minio import Minio
from dotenv import load_dotenv
import os

from scrapers.utils import setup_logger, retry, ArticleDeduplicator

load_dotenv()
logger = setup_logger("scrapers")


class BaseScraper(ABC):
    """Classe abstraite pour tous les scrapers de news."""

    def __init__(self, source_name: str, base_url: str, language: str, country: str):
        self.source_name = source_name
        self.base_url = base_url
        self.language = language
        self.country = country

        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        }

        # Client MinIO
        self.minio_client = Minio(
            os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
            secure=False
        )
        self.bronze_bucket = os.getenv('BUCKET_BRONZE', 'bronze')
        if not self.minio_client.bucket_exists(self.bronze_bucket):
            self.minio_client.make_bucket(self.bronze_bucket)
            logger.info(f"✅ Bucket créé : {self.bronze_bucket}")

        # Déduplicator
        self.deduplicator = ArticleDeduplicator()

        # Stats
        self.stats = {
            'total_links_found': 0,
            'duplicates_skipped': 0,
            'errors': 0,
            'success': 0,
        }

        logger.info(f"✅ Scraper {self.source_name} initialisé")

    @retry(max_attempts=3, delay=2.0)
    def fetch_page(self, url: str, timeout: int = 15) -> BeautifulSoup | None:
        """Télécharge une page web (avec retry automatique)."""
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return BeautifulSoup(response.text, 'lxml')
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️  Timeout sur {url}")
            raise
        except requests.exceptions.HTTPError as e:
            # Pas de retry pour les 4xx (paywall, not found, etc.)
            if e.response.status_code in (402, 403, 404):
                logger.error(f"❌ {e.response.status_code} bloquant pour {url}")
                return None
            raise
        except Exception as e:
            logger.error(f"Erreur fetch {url}: {e}")
            raise

    def generate_article_id(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    def save_to_bronze(self, articles: list) -> str:
        if not articles:
            logger.warning("Aucun article à sauvegarder")
            return ""

        now = datetime.now()
        timestamp = int(now.timestamp())
        filename = (
            f"{self.source_name}/{now.year}/{now.month:02d}/{now.day:02d}/"
            f"{self.source_name}_{timestamp}.json"
        )

        payload = {
            'source': self.source_name,
            'language': self.language,
            'country': self.country,
            'scrape_timestamp': timestamp,
            'scrape_datetime': now.isoformat(),
            'article_count': len(articles),
            'articles': articles,
        }
        json_data = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')

        self.minio_client.put_object(
            self.bronze_bucket,
            filename,
            BytesIO(json_data),
            len(json_data),
            content_type='application/json'
        )
        logger.success(f"💾 {len(articles)} articles → bronze/{filename}")
        return filename

    @abstractmethod
    def get_article_links(self, max_articles: int = 10) -> list:
        pass

    @abstractmethod
    def parse_article(self, url: str) -> dict | None:
        pass

    def run(self, max_articles: int = 10, delay: float = 1.0) -> dict:
        """Pipeline complet avec gestion d'erreurs et déduplication."""
        logger.info(f"🚀 Lancement du scraper {self.source_name}")
        start_time = time.time()

        # 1. Récupérer les liens
        try:
            links = self.get_article_links(max_articles=max_articles)
        except Exception as e:
            logger.error(f"❌ Échec récupération des liens : {e}")
            return self.stats

        self.stats['total_links_found'] = len(links)
        logger.info(f"📋 {len(links)} liens trouvés")

        # 2. Dédupliquer AVANT de parser (économise du temps)
        new_links = []
        for link in links:
            article_id = self.generate_article_id(link)
            if self.deduplicator.is_duplicate(article_id):
                self.stats['duplicates_skipped'] += 1
                logger.debug(f"⏭️  Skip doublon : {link}")
            else:
                new_links.append(link)

        if not new_links:
            logger.info(f"✨ Aucun nouveau lien (tous déjà scrapés)")
            return self.stats

        logger.info(f"🆕 {len(new_links)} nouveaux articles à parser")

        # 3. Parser chaque article
        articles = []
        for i, link in enumerate(new_links, 1):
            logger.info(f"  [{i}/{len(new_links)}] {link}")
            try:
                article = self.parse_article(link)
                if article:
                    article_id = self.generate_article_id(link)
                    article['article_id'] = article_id
                    article['source'] = self.source_name
                    article['language'] = self.language
                    article['country'] = self.country
                    article['scraped_at'] = datetime.now().isoformat()
                    articles.append(article)
                    self.deduplicator.mark_seen(article_id)
                    self.stats['success'] += 1
                else:
                    self.stats['errors'] += 1
            except Exception as e:
                logger.error(f"Erreur parsing {link}: {e}")
                self.stats['errors'] += 1
            
            time.sleep(delay)

        # 4. Sauvegarder
        if articles:
            self.save_to_bronze(articles)

        # 5. Rapport final
        duration = time.time() - start_time
        logger.success(
            f"🎉 {self.source_name} terminé en {duration:.1f}s | "
            f"✅ {self.stats['success']} | "
            f"⏭️  {self.stats['duplicates_skipped']} doublons | "
            f"❌ {self.stats['errors']} erreurs"
        )
        return self.stats