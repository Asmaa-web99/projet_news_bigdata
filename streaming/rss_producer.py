"""
RSS Producer Kafka : surveille les flux RSS de news en continu
et publie chaque nouvel article dans Kafka.
"""
import sys
import os
import json
import time
import hashlib
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import feedparser
from kafka import KafkaProducer
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# ===== Configuration des flux RSS =====
RSS_FEEDS = {
    "bbc_world": {
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "source": "bbc",
        "language": "en",
        "country": "UK",
    },
    "aljazeera": {
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "source": "aljazeera",
        "language": "en",
        "country": "QA",
    },
    "franceinfo": {
        "url": "https://www.francetvinfo.fr/titres.rss",
        "source": "franceinfo",
        "language": "fr",
        "country": "FR",
    },
    "hespress": {
        "url": "https://fr.hespress.com/feed",
        "source": "hespress",
        "language": "fr",
        "country": "MA",
    },
}


class RSSStreamProducer:
    """Producer Kafka pour les flux RSS de news."""

    def __init__(self):
        self.kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
        self.topic = os.getenv('KAFKA_TOPIC_NEWS', 'news_streaming')
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[self.kafka_broker],
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                api_version_auto_timeout_ms=10000,
                request_timeout_ms=30000,
                connections_max_idle_ms=30000,
            )
        except Exception as e:
            logger.error(f"❌ Erreur de connexion à Kafka ({self.kafka_broker}): {e}")
            logger.error("Assurez-vous que Kafka est en cours d'exécution: docker-compose up -d")
            raise
        
        # Cache déduplication (en mémoire pour cette session)
        self.seen_articles = set()
        logger.info(f"✅ Producer Kafka initialisé. Topic : {self.topic}")

    def fetch_rss(self, feed_name: str, feed_config: dict) -> list:
        """Récupère les articles d'un flux RSS."""
        try:
            feed = feedparser.parse(feed_config['url'])
            entries = feed.entries
            logger.info(f"  📰 {feed_name} : {len(entries)} entrées")
            return entries
        except Exception as e:
            logger.error(f"❌ Erreur RSS {feed_name}: {e}")
            return []

    def article_to_event(self, entry, feed_config: dict) -> dict:
        """Convertit un entry RSS en événement Kafka structuré."""
        url = entry.get('link', '')
        article_id = hashlib.md5(url.encode()).hexdigest()
        
        description = entry.get('summary', '') or entry.get('description', '')
        
        return {
            'article_id': article_id,
            'source': feed_config['source'],
            'language': feed_config['language'],
            'country': feed_config['country'],
            'title': entry.get('title', 'No title'),
            'url': url,
            'description': description[:500],  # Limite pour Kafka
            'publication_date': entry.get('published', ''),
            'event_timestamp': datetime.now().isoformat(),
            'event_type': 'rss_streaming',
        }

    def publish(self, event: dict) -> bool:
        """Publie un événement dans Kafka."""
        try:
            key = event['source']  # Partitionnement par source
            future = self.producer.send(self.topic, key=key, value=event)
            future.get(timeout=10)
            return True
        except Exception as e:
            logger.error(f"❌ Erreur publish : {e}")
            return False

    def stream_once(self) -> int:
        """Une passe complète : lit tous les RSS et publie les nouveaux."""
        new_count = 0
        for feed_name, feed_config in RSS_FEEDS.items():
            entries = self.fetch_rss(feed_name, feed_config)
            for entry in entries:
                event = self.article_to_event(entry, feed_config)
                
                # Dédupliquer
                if event['article_id'] in self.seen_articles:
                    continue
                
                if self.publish(event):
                    self.seen_articles.add(event['article_id'])
                    new_count += 1
                    logger.info(f"    ✨ [{event['source']}] {event['title'][:70]}")
        
        return new_count

    def run_continuous(self, interval_seconds: int = 60, max_iterations: int = None):
        """Boucle : surveille les RSS toutes les X secondes."""
        logger.info(f"🚀 Streaming RSS démarré (intervalle : {interval_seconds}s)")
        iteration = 0
        try:
            while True:
                iteration += 1
                logger.info(f"\n{'='*50}")
                logger.info(f"🔄 ITÉRATION {iteration}")
                logger.info(f"{'='*50}")
                
                new_articles = self.stream_once()
                logger.success(
                    f"✅ {new_articles} nouveaux articles publiés "
                    f"(cache total : {len(self.seen_articles)})"
                )
                
                if max_iterations and iteration >= max_iterations:
                    logger.info("Limite atteinte, arrêt.")
                    break
                
                logger.info(f"⏳ Attente {interval_seconds}s...")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.warning("\n⚠️ Arrêt utilisateur")
        finally:
            self.producer.flush()
            self.producer.close()
            logger.info("Producer fermé.")


if __name__ == "__main__":
    producer = RSSStreamProducer()
    # Mode test : 2 itérations de 30s
    producer.run_continuous(interval_seconds=30, max_iterations=2)