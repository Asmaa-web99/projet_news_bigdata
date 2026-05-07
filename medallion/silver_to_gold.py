"""
Pipeline Silver → Gold
Lit les articles enrichis de Silver et crée des tables analytiques agrégées.
"""
import sys
import os
from io import BytesIO
from datetime import datetime
from collections import Counter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from minio import Minio
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class SilverToGoldPipeline:
    """Pipeline Silver → Gold : agrégations analytiques."""

    def __init__(self):
        self.minio_client = Minio(
            os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
            secure=False
        )
        self.silver_bucket = os.getenv('BUCKET_SILVER', 'silver')
        self.gold_bucket = os.getenv('BUCKET_GOLD', 'gold')
        logger.info("✅ Pipeline Silver → Gold initialisé")

    def read_silver_data(self) -> pd.DataFrame:
        """Lit tous les fichiers Parquet du bucket Silver et les concatène."""
        objects = list(self.minio_client.list_objects(
            self.silver_bucket, recursive=True
        ))
        parquet_files = [obj.object_name for obj in objects if obj.object_name.endswith('.parquet')]
        
        if not parquet_files:
            logger.warning("Aucun fichier Parquet dans Silver")
            return pd.DataFrame()

        logger.info(f"📂 {len(parquet_files)} fichiers Silver trouvés")
        
        all_dfs = []
        for pf in parquet_files:
            try:
                response = self.minio_client.get_object(self.silver_bucket, pf)
                df = pd.read_parquet(BytesIO(response.read()))
                response.close()
                response.release_conn()
                all_dfs.append(df)
            except Exception as e:
                logger.error(f"Erreur lecture {pf}: {e}")

        if not all_dfs:
            return pd.DataFrame()
        
        full_df = pd.concat(all_dfs, ignore_index=True)
        # Dédupliquer sur article_id
        full_df = full_df.drop_duplicates(subset=['article_id'], keep='last')
        logger.info(f"📊 Dataset Silver consolidé : {len(full_df)} articles uniques")
        return full_df

    def save_to_gold(self, df: pd.DataFrame, table_name: str) -> str:
        """Sauvegarde une table Gold en Parquet."""
        if df.empty:
            logger.warning(f"Table {table_name} vide, ignorée")
            return ""

        buffer = BytesIO()
        df.to_parquet(buffer, engine='pyarrow', compression='snappy', index=False)
        buffer.seek(0)
        data = buffer.getvalue()

        timestamp = int(datetime.now().timestamp())
        filename = f"{table_name}/{table_name}_{timestamp}.parquet"

        self.minio_client.put_object(
            self.gold_bucket,
            filename,
            BytesIO(data),
            len(data),
            content_type='application/octet-stream'
        )
        logger.success(f"✅ Table '{table_name}' ({len(df)} lignes) → gold/{filename}")
        return filename

    # =========================================================================
    # TABLES ANALYTIQUES
    # =========================================================================

    def build_articles_by_source(self, df: pd.DataFrame) -> pd.DataFrame:
        """Table : Nombre d'articles par source."""
        result = df.groupby(['source', 'country', 'language']).agg(
            total_articles=('article_id', 'count'),
            avg_word_count=('word_count', 'mean'),
            total_words=('word_count', 'sum'),
            unique_categories=('category', 'nunique'),
        ).reset_index()
        result['avg_word_count'] = result['avg_word_count'].round(1)
        return result.sort_values('total_articles', ascending=False)

    def build_articles_by_language(self, df: pd.DataFrame) -> pd.DataFrame:
        """Table : Distribution par langue."""
        result = df.groupby('language').agg(
            total_articles=('article_id', 'count'),
            sources_count=('source', 'nunique'),
            avg_words=('word_count', 'mean'),
        ).reset_index()
        result['avg_words'] = result['avg_words'].round(1)
        return result.sort_values('total_articles', ascending=False)

    def build_articles_by_country(self, df: pd.DataFrame) -> pd.DataFrame:
        """Table : Articles par pays."""
        result = df.groupby('country').agg(
            total_articles=('article_id', 'count'),
            sources_list=('source', lambda x: ', '.join(sorted(x.unique()))),
        ).reset_index()
        return result.sort_values('total_articles', ascending=False)

    def build_articles_by_category(self, df: pd.DataFrame) -> pd.DataFrame:
        """Table : Articles par catégorie."""
        result = df.groupby(['source', 'category']).agg(
            total_articles=('article_id', 'count'),
            avg_words=('word_count', 'mean'),
        ).reset_index()
        result['avg_words'] = result['avg_words'].round(1)
        return result.sort_values(['source', 'total_articles'], ascending=[True, False])

    def build_top_keywords(self, df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
        """Table : Top des mots-clés tendances."""
        all_keywords = []
        for kw_list in df['keywords']:
            if isinstance(kw_list, (list, tuple)) or hasattr(kw_list, '__iter__'):
                all_keywords.extend([str(k).lower() for k in kw_list if k])

        if not all_keywords:
            return pd.DataFrame(columns=['keyword', 'frequency'])

        counter = Counter(all_keywords)
        top = counter.most_common(top_n)
        return pd.DataFrame(top, columns=['keyword', 'frequency'])

    def build_top_keywords_by_language(self, df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
        """Table : Top mots-clés par langue (pour analyse multilingue)."""
        rows = []
        for lang in df['language'].unique():
            lang_df = df[df['language'] == lang]
            kws = []
            for kw_list in lang_df['keywords']:
                if hasattr(kw_list, '__iter__'):
                    kws.extend([str(k).lower() for k in kw_list if k])
            for kw, freq in Counter(kws).most_common(top_n):
                rows.append({'language': lang, 'keyword': kw, 'frequency': freq})
        return pd.DataFrame(rows)

    def build_global_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Table : Statistiques globales du dataset."""
        stats = {
            'metric': [
                'total_articles',
                'total_sources',
                'total_languages',
                'total_countries',
                'total_words',
                'avg_words_per_article',
                'min_words',
                'max_words',
            ],
            'value': [
                len(df),
                df['source'].nunique(),
                df['language'].nunique(),
                df['country'].nunique(),
                int(df['word_count'].sum()),
                round(df['word_count'].mean(), 1),
                int(df['word_count'].min()),
                int(df['word_count'].max()),
            ]
        }
        return pd.DataFrame(stats)

    def run(self):
        """Exécute toutes les agrégations Silver → Gold."""
        logger.info("🚀 Démarrage Pipeline Silver → Gold")

        # 1. Lire Silver
        df = self.read_silver_data()
        if df.empty:
            logger.warning("Pas de données Silver à traiter")
            return

        # 2. Construire toutes les tables analytiques
        logger.info("\n📊 Construction des tables analytiques :")

        tables = {
            'articles_by_source': self.build_articles_by_source(df),
            'articles_by_language': self.build_articles_by_language(df),
            'articles_by_country': self.build_articles_by_country(df),
            'articles_by_category': self.build_articles_by_category(df),
            'top_keywords': self.build_top_keywords(df, top_n=50),
            'top_keywords_by_language': self.build_top_keywords_by_language(df, top_n=15),
            'global_stats': self.build_global_stats(df),
        }

        # 3. Sauvegarder chaque table
        for name, table_df in tables.items():
            if not table_df.empty:
                logger.info(f"\n  📋 Table : {name}")
                logger.info(f"\n{table_df.head(10).to_string(index=False)}\n")
                self.save_to_gold(table_df, name)

        # 4. Sauvegarder aussi le dataset complet enrichi en Gold (pour le DWH)
        # Sans la colonne 'keywords' (liste) qui pose problème en SQL
        df_for_dwh = df.copy()
        if 'keywords' in df_for_dwh.columns:
            df_for_dwh = df_for_dwh.drop(columns=['keywords'])
        self.save_to_gold(df_for_dwh, 'fact_articles')

        logger.success(f"🎉 Pipeline Gold terminé : {len(tables) + 1} tables créées")


if __name__ == "__main__":
    pipeline = SilverToGoldPipeline()
    pipeline.run()