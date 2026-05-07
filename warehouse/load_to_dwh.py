"""
ETL final : Gold (MinIO Parquet) → Data Warehouse (PostgreSQL).
Charge les articles enrichis dans le Star Schema.
"""
import sys
import os
from io import BytesIO
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from minio import Minio
from sqlalchemy import create_engine, text
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class GoldToDWHLoader:
    """Charge les tables Gold dans le Data Warehouse PostgreSQL."""

    def __init__(self):
        # Client MinIO
        self.minio_client = Minio(
            os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
            secure=False
        )
        self.gold_bucket = os.getenv('BUCKET_GOLD', 'gold')

        # Connection PostgreSQL via SQLAlchemy
        dwh_url = (
            f"postgresql://{os.getenv('DWH_USER')}:{os.getenv('DWH_PASSWORD')}"
            f"@{os.getenv('DWH_HOST')}:{os.getenv('DWH_PORT')}"
            f"/{os.getenv('DWH_DATABASE')}"
        )
        self.engine = create_engine(dwh_url)
        logger.info("✅ Loader DWH initialisé")

    def read_gold_table(self, table_name: str) -> pd.DataFrame:
        """Lit la dernière version d'une table Gold depuis MinIO."""
        objects = list(self.minio_client.list_objects(
            self.gold_bucket, prefix=f"{table_name}/", recursive=True
        ))
        parquet_files = [obj for obj in objects if obj.object_name.endswith('.parquet')]
        
        if not parquet_files:
            logger.warning(f"Aucun fichier pour la table {table_name}")
            return pd.DataFrame()

        # Prendre le plus récent
        latest = max(parquet_files, key=lambda o: o.last_modified)
        logger.info(f"  📄 Lecture : {latest.object_name}")

        response = self.minio_client.get_object(self.gold_bucket, latest.object_name)
        df = pd.read_parquet(BytesIO(response.read()))
        response.close()
        response.release_conn()
        return df

    def get_source_id_map(self) -> dict:
        """Récupère le mapping source_name → source_id depuis dim_source."""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT source_id, source_name FROM dim_source"))
            return {row.source_name: row.source_id for row in result}

    def get_language_id_map(self) -> dict:
        """Récupère le mapping language_code → language_id depuis dim_language."""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT language_id, language_code FROM dim_language"))
            return {row.language_code: row.language_id for row in result}

    def upsert_date(self, date_value: datetime.date) -> int:
        """Insère une date dans dim_date si absente, retourne son ID."""
        with self.engine.begin() as conn:
            # Vérifier si existe
            result = conn.execute(
                text("SELECT date_id FROM dim_date WHERE date_value = :d"),
                {"d": date_value}
            ).fetchone()
            if result:
                return result.date_id

            # Insérer
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                         'Friday', 'Saturday', 'Sunday']
            day_of_week = day_names[date_value.weekday()]
            quarter = (date_value.month - 1) // 3 + 1

            result = conn.execute(text("""
                INSERT INTO dim_date (date_value, year, month, day, day_of_week, quarter)
                VALUES (:dv, :y, :m, :d, :dow, :q)
                RETURNING date_id
            """), {
                "dv": date_value,
                "y": date_value.year,
                "m": date_value.month,
                "d": date_value.day,
                "dow": day_of_week,
                "q": quarter,
            }).fetchone()
            return result.date_id

    def load_fact_articles(self):
        """Charge la table fact_articles depuis Gold vers DWH."""
        logger.info("🔄 Chargement de fact_articles...")

        df = self.read_gold_table('fact_articles')
        if df.empty:
            logger.warning("Pas de données dans Gold")
            return

        logger.info(f"  📊 {len(df)} articles à charger")

        # Récupérer les mappings de dimensions
        source_map = self.get_source_id_map()
        language_map = self.get_language_id_map()
        logger.info(f"  Sources connues : {list(source_map.keys())}")
        logger.info(f"  Langues connues : {list(language_map.keys())}")

        # Préparer les données
        rows_to_insert = []
        skipped = 0

        for _, row in df.iterrows():
            source_id = source_map.get(row.get('source'))
            language_id = language_map.get(row.get('language', 'unknown'),
                                           language_map.get('unknown'))

            if not source_id:
                skipped += 1
                continue

            # Date : utiliser scraped_at ou today
            try:
                if row.get('scraped_at'):
                    date_obj = datetime.fromisoformat(str(row['scraped_at']).split('T')[0]).date()
                else:
                    date_obj = datetime.now().date()
            except Exception:
                date_obj = datetime.now().date()

            date_id = self.upsert_date(date_obj)

            # scraped_at en timestamp pour la BD
            try:
                scraped_ts = pd.to_datetime(row.get('scraped_at')) if row.get('scraped_at') else None
            except Exception:
                scraped_ts = None

            rows_to_insert.append({
                'article_id': str(row['article_id']),
                'source_id': source_id,
                'date_id': date_id,
                'language_id': language_id,
                'title': str(row.get('title', ''))[:1000],  # Truncate
                'author': str(row.get('author', ''))[:255],
                'category': str(row.get('category', ''))[:100],
                'url': str(row.get('url', '')),
                'content': str(row.get('content', '')),
                'word_count': int(row.get('word_count', 0)),
                'char_count': int(row.get('char_count', 0)),
                'sentence_count': int(row.get('sentence_count', 0)),
                'keywords_str': str(row.get('keywords_str', '')),
                'sentiment_score': float(row.get('sentiment_score', 0.0)),
                'sentiment_label': str(row.get('sentiment_label', 'neutral'))[:20],
                'positive_words_count': int(row.get('positive_words_count', 0)),
                'negative_words_count': int(row.get('negative_words_count', 0)),
                'publication_date': str(row.get('publication_date', ''))[:50],
                'scraped_at': scraped_ts,
            })

        if not rows_to_insert:
            logger.warning("Aucune ligne à insérer")
            return

        # UPSERT en lot avec ON CONFLICT
        with self.engine.begin() as conn:
            # Vider d'abord pour éviter les doublons (mode "full reload")
            conn.execute(text("TRUNCATE TABLE fact_articles"))
            
            insert_sql = text("""
                INSERT INTO fact_articles (
                    article_id, source_id, date_id, language_id,
                    title, author, category, url, content,
                    word_count, char_count, sentence_count,
                    keywords_str, sentiment_score, sentiment_label,
                    positive_words_count, negative_words_count,
                    publication_date, scraped_at
                ) VALUES (
                    :article_id, :source_id, :date_id, :language_id,
                    :title, :author, :category, :url, :content,
                    :word_count, :char_count, :sentence_count,
                    :keywords_str, :sentiment_score, :sentiment_label,
                    :positive_words_count, :negative_words_count,
                    :publication_date, :scraped_at
                )
                ON CONFLICT (article_id) DO NOTHING
            """)
            conn.execute(insert_sql, rows_to_insert)

        logger.success(f"✅ {len(rows_to_insert)} articles chargés (ignorés : {skipped})")

    def run(self):
        """Pipeline complet ETL : Gold → DWH."""
        logger.info("🚀 Démarrage chargement Gold → DWH")
        self.load_fact_articles()
        
        # Statistiques finales
        with self.engine.connect() as conn:
            stats = conn.execute(text("""
                SELECT 
                    COUNT(*) AS total_articles,
                    COUNT(DISTINCT source_id) AS sources,
                    COUNT(DISTINCT language_id) AS languages,
                    COUNT(DISTINCT date_id) AS dates,
                    SUM(word_count) AS total_words
                FROM fact_articles
            """)).fetchone()
            logger.info(f"\n📊 Statistiques DWH :")
            logger.info(f"   • Articles  : {stats.total_articles}")
            logger.info(f"   • Sources   : {stats.sources}")
            logger.info(f"   • Langues   : {stats.languages}")
            logger.info(f"   • Dates     : {stats.dates}")
            logger.info(f"   • Mots tot. : {stats.total_words}")

        logger.success("🎉 Pipeline DWH terminé !")


if __name__ == "__main__":
    loader = GoldToDWHLoader()
    loader.run()