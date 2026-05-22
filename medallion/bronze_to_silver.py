"""
Pipeline Bronze → Silver
Lit les articles bruts dans Bronze, applique nettoyage + NLP, 
et sauvegarde en Parquet dans Silver.
"""
import sys
import os
import json
from io import BytesIO
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from minio import Minio
from loguru import logger
from dotenv import load_dotenv

from medallion.nlp_utils import (
    clean_html,
    detect_language,
    extract_keywords,
    compute_text_stats,
    is_valid_article,
    analyze_sentiment,
)

load_dotenv()


class BronzeToSilverPipeline:
    """Pipeline de transformation Bronze → Silver avec NLP."""

    def __init__(self):
        self.minio_client = Minio(
            os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
            secure=False
        )
        self.bronze_bucket = os.getenv('BUCKET_BRONZE', 'bronze')
        self.silver_bucket = os.getenv('BUCKET_SILVER', 'silver')
        for bucket in [self.bronze_bucket, self.silver_bucket]:
            if not self.minio_client.bucket_exists(bucket):
                self.minio_client.make_bucket(bucket)
                logger.info(f"✅ Bucket créé : {bucket}")
        logger.info("✅ Pipeline Bronze → Silver initialisé")

    def list_bronze_files(self) -> list:
        """Liste tous les fichiers JSON dans le bucket bronze."""
        objects = self.minio_client.list_objects(
            self.bronze_bucket, recursive=True
        )
        files = [obj.object_name for obj in objects if obj.object_name.endswith('.json')]
        logger.info(f"📂 {len(files)} fichiers Bronze trouvés")
        return files

    def read_bronze_file(self, file_path: str) -> dict:
        """Lit un fichier JSON depuis le bucket bronze."""
        try:
            response = self.minio_client.get_object(self.bronze_bucket, file_path)
            data = json.loads(response.read().decode('utf-8'))
            response.close()
            response.release_conn()
            return data
        except Exception as e:
            logger.error(f"Erreur lecture {file_path}: {e}")
            return {}

    def transform_article(self, article: dict, source_metadata: dict) -> dict | None:
        """
        Applique toutes les transformations Silver à un article.
        Retourne un dict enrichi ou None si invalide.
        """
        # Validation
        if not is_valid_article(article, min_words=20):
            return None

        # 1. Nettoyage HTML
        clean_title = clean_html(article.get('title', ''))
        clean_content = clean_html(article.get('content', ''))

        # 2. Détection de langue (depuis le contenu)
        detected_lang = detect_language(clean_content)
        # Garder la langue déclarée si la détection échoue
        final_lang = detected_lang if detected_lang != "unknown" else article.get('language', 'unknown')

        # 3. Extraction de mots-clés
        keywords = extract_keywords(
            text=f"{clean_title}. {clean_content}",
            language=final_lang,
            top_n=10
        )

        # 4. Statistiques
        stats = compute_text_stats(clean_content)

        # 4.5 Analyse de sentiment (NOUVEAU) - avec fallback
        try:
            sentiment = analyze_sentiment(
                text=f"{clean_title}. {clean_content}",
                language=final_lang
            )
            # Fallback si résultat invalide
            if not sentiment or 'label' not in sentiment:
                sentiment = {'score': 0.0, 'label': 'neutral', 'positive_count': 0, 'negative_count': 0}
        except Exception as e:
            logger.debug(f"Sentiment analysis failed for article {article.get('article_id', 'unknown')}: {e}")
            # Fallback: sentiment neutre par défaut
            sentiment = {'score': 0.0, 'label': 'neutral', 'positive_count': 0, 'negative_count': 0}

        # 5. Construction de l'enregistrement Silver
        return {
            'article_id': article.get('article_id', ''),
            'source': article.get('source', source_metadata.get('source', '')),
            'country': article.get('country', source_metadata.get('country', '')),
            'declared_language': article.get('language', ''),
            'detected_language': detected_lang,
            'language': final_lang,
            'url': article.get('url', ''),
            'title': clean_title,
            'author': article.get('author', 'Inconnu'),
            'category': article.get('category', 'Général'),
            'publication_date': article.get('publication_date', ''),
            'scraped_at': article.get('scraped_at', ''),
            'content': clean_content,
            'word_count': stats['word_count'],
            'char_count': stats['char_count'],
            'sentence_count': stats['sentence_count'],
            'keywords': keywords,
            'keywords_str': ', '.join(keywords),  # version string pour SQL
            'sentiment_score': sentiment['score'],
            'sentiment_label': sentiment['label'],
            'positive_words_count': sentiment['positive_count'],
            'negative_words_count': sentiment['negative_count'],
            'processed_at': datetime.now().isoformat(),
        }

    def save_to_silver(self, df: pd.DataFrame, partition_date: str) -> str:
        """Sauvegarde le DataFrame en format Parquet dans Silver."""
        if df.empty:
            logger.warning("DataFrame vide, rien à sauvegarder")
            return ""

        # Format Parquet (optimisé pour analytics)
        buffer = BytesIO()
        df.to_parquet(buffer, engine='pyarrow', compression='snappy', index=False)
        buffer.seek(0)
        data = buffer.getvalue()

        # Path partitionné par date
        timestamp = int(datetime.now().timestamp())
        filename = f"articles/date={partition_date}/articles_{timestamp}.parquet"

        self.minio_client.put_object(
            self.silver_bucket,
            filename,
            BytesIO(data),
            len(data),
            content_type='application/octet-stream'
        )
        logger.success(f"✅ {len(df)} articles → silver/{filename}")
        return filename

    def run(self):
        """Exécute le pipeline complet Bronze → Silver."""
        logger.info("🚀 Démarrage Pipeline Bronze → Silver")

        # 1. Lister tous les fichiers Bronze
        bronze_files = self.list_bronze_files()
        if not bronze_files:
            logger.warning("Aucun fichier Bronze à traiter")
            return

        # 2. Lire et transformer
        all_silver_records = []
        for bronze_file in bronze_files:
            logger.info(f"  📄 Traitement : {bronze_file}")
            data = self.read_bronze_file(bronze_file)
            if not data:
                continue

            articles = data.get('articles', [])
            source_meta = {
                'source': data.get('source', ''),
                'country': data.get('country', ''),
            }

            for article in articles:
                silver_record = self.transform_article(article, source_meta)
                if silver_record:
                    all_silver_records.append(silver_record)

        if not all_silver_records:
            logger.warning("Aucun article valide après transformation")
            return

        # 3. Construire un DataFrame
        df = pd.DataFrame(all_silver_records)
        logger.info(f"📊 DataFrame Silver : {len(df)} articles, {len(df.columns)} colonnes")
        logger.info(f"   Sources : {df['source'].value_counts().to_dict()}")
        logger.info(f"   Langues : {df['language'].value_counts().to_dict()}")

        # 4. Sauvegarder en Parquet partitionné par date
        partition_date = datetime.now().strftime("%Y-%m-%d")
        self.save_to_silver(df, partition_date)
        logger.success(f"🎉 Pipeline Silver terminé : {len(df)} articles transformés")


if __name__ == "__main__":
    pipeline = BronzeToSilverPipeline()
    pipeline.run()