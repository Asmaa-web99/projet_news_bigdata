"""
Script global : lance TOUS les scrapers en séquence.
"""
import sys
import time
from datetime import datetime

sys.path.append('.')

from scrapers.hespress_scraper import HespressScraper
from scrapers.bbc_scraper import BBCScraper
from scrapers.akhbarona_scraper import AkhbaronaScraper
from scrapers.aljazeera_scraper import AlJazeeraScraper
from scrapers.franceinfo_scraper import FranceInfoScraper

from loguru import logger


def run_all_scrapers(max_articles: int = 20, delay: float = 1.5):
    """Exécute tous les scrapers et affiche un rapport global."""
    
    scrapers = [
        ('Hespress (FR/MA)', HespressScraper),
        ('BBC News (EN/UK)', BBCScraper),
        ('Akhbarona (AR/MA)', AkhbaronaScraper),
        ('Al Jazeera (EN/QA)', AlJazeeraScraper),
        ('France Info (FR/FR)', FranceInfoScraper),
    ]

    logger.info("=" * 60)
    logger.info(f"🚀 LANCEMENT GLOBAL DE {len(scrapers)} SCRAPERS")
    logger.info(f"   Max articles par source : {max_articles}")
    logger.info(f"   Démarré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    global_stats = {
        'total_success': 0,
        'total_duplicates': 0,
        'total_errors': 0,
        'sources_completed': 0,
        'sources_failed': 0,
    }

    start_time = time.time()

    for name, ScraperClass in scrapers:
        logger.info(f"\n{'─' * 60}")
        logger.info(f"📰 SCRAPER : {name}")
        logger.info(f"{'─' * 60}")
        
        try:
            scraper = ScraperClass()
            stats = scraper.run(max_articles=max_articles, delay=delay)
            global_stats['total_success'] += stats.get('success', 0)
            global_stats['total_duplicates'] += stats.get('duplicates_skipped', 0)
            global_stats['total_errors'] += stats.get('errors', 0)
            global_stats['sources_completed'] += 1
        except Exception as e:
            logger.error(f"❌ Échec total de {name}: {e}")
            global_stats['sources_failed'] += 1

    duration = time.time() - start_time

    # Rapport final
    logger.info("\n" + "=" * 60)
    logger.info("📊 RAPPORT GLOBAL")
    logger.info("=" * 60)
    logger.info(f"⏱️  Durée totale : {duration:.1f}s ({duration/60:.1f} min)")
    logger.info(f"✅ Sources réussies : {global_stats['sources_completed']}/{len(scrapers)}")
    logger.info(f"❌ Sources échouées : {global_stats['sources_failed']}")
    logger.info(f"📰 Articles scrapés : {global_stats['total_success']}")
    logger.info(f"⏭️  Doublons skippés : {global_stats['total_duplicates']}")
    logger.info(f"⚠️  Erreurs articles : {global_stats['total_errors']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_all_scrapers(max_articles=20, delay=1.5)