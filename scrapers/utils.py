"""
Utilitaires partagés pour les scrapers : logs, retry, déduplication.
"""
import os
import sys
import time
from functools import wraps
from datetime import datetime
from pathlib import Path
from loguru import logger


# ============================================================
# CONFIGURATION DES LOGS PERSISTÉS
# ============================================================

def setup_logger(module_name: str = "scraper"):
    """Configure les logs : console + fichier rotatif."""
    # Supprimer le handler par défaut
    logger.remove()
    
    # Console (toujours actif)
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # Fichier rotatif (nouveau fichier chaque jour, gardés 7 jours)
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{module_name}_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    logger.add(
        str(log_file),
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}",
        encoding="utf-8"
    )
    
    return logger


# ============================================================
# DÉCORATEUR RETRY (gestion d'erreurs réseau)
# ============================================================

def retry(max_attempts: int = 3, delay: float = 2.0, backoff: float = 2.0):
    """
    Décorateur qui retry une fonction en cas d'erreur.
    
    Args:
        max_attempts: nombre maximum de tentatives
        delay: délai initial entre tentatives (secondes)
        backoff: multiplicateur du délai à chaque échec
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"⚠️  Tentative {attempt}/{max_attempts} échouée pour {func.__name__}: {e}. "
                            f"Retry dans {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"❌ Toutes les tentatives ont échoué pour {func.__name__}")
            
            # Si toutes les tentatives ont échoué
            raise last_exception
        return wrapper
    return decorator


# ============================================================
# DÉDUPLICATION (cache des article_ids déjà scrapés)
# ============================================================

class ArticleDeduplicator:
    """
    Gère la déduplication des articles via un fichier cache.
    Évite de re-scraper les mêmes articles à chaque exécution.
    """

    def __init__(self, cache_file: str = "logs/seen_articles.txt"):
        self.cache_file = Path(__file__).parent.parent / cache_file
        self.cache_file.parent.mkdir(exist_ok=True)
        self.seen_ids = self._load_cache()

    def _load_cache(self) -> set:
        """Charge le cache depuis le disque."""
        if not self.cache_file.exists():
            return set()
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        except Exception as e:
            logger.warning(f"Erreur lecture cache : {e}")
            return set()

    def is_duplicate(self, article_id: str) -> bool:
        """Vérifie si un article_id a déjà été scrapé."""
        return article_id in self.seen_ids

    def mark_seen(self, article_id: str):
        """Marque un article comme vu et persiste."""
        if article_id not in self.seen_ids:
            self.seen_ids.add(article_id)
            with open(self.cache_file, 'a', encoding='utf-8') as f:
                f.write(f"{article_id}\n")

    def clear(self):
        """Vide le cache (utile pour les tests)."""
        self.seen_ids.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("🗑️ Cache de déduplication vidé")

    def stats(self) -> dict:
        """Retourne des statistiques sur le cache."""
        return {
            'total_seen': len(self.seen_ids),
            'cache_file': str(self.cache_file),
            'size_kb': self.cache_file.stat().st_size / 1024 if self.cache_file.exists() else 0
        }