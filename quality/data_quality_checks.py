"""
Framework de Qualité des Données
Inspiré de Great Expectations — Tests automatisés sur Bronze, Silver et DWH.
Dimensions testées : Complétude, Cohérence, Validité, Fraîcheur.
"""
import sys
import os
import json
from io import BytesIO
from datetime import datetime, timedelta
from collections import defaultdict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from minio import Minio
from sqlalchemy import create_engine, text
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class DataQualityResult:
    """Résultat d'un test de qualité."""
    
    def __init__(self, test_name: str, dimension: str, layer: str):
        self.test_name = test_name
        self.dimension = dimension  # completude, coherence, validite, fraicheur
        self.layer = layer          # bronze, silver, gold, dwh
        self.passed = False
        self.total_records = 0
        self.failed_records = 0
        self.success_rate = 0.0
        self.details = ""
        self.timestamp = datetime.now().isoformat()
    
    def evaluate(self, total: int, failed: int, threshold: float = 0.95):
        """Évalue le test : passe si le taux de succès >= threshold."""
        self.total_records = total
        self.failed_records = failed
        if total > 0:
            self.success_rate = (total - failed) / total
        else:
            self.success_rate = 0.0
        self.passed = self.success_rate >= threshold
    
    def to_dict(self) -> dict:
        return {
            'test_name': self.test_name,
            'dimension': self.dimension,
            'layer': self.layer,
            'passed': '✅ PASS' if self.passed else '❌ FAIL',
            'total_records': self.total_records,
            'failed_records': self.failed_records,
            'success_rate': f"{self.success_rate:.1%}",
            'details': self.details,
            'timestamp': self.timestamp,
        }


class DataQualityFramework:
    """Framework complet de tests de qualité."""

    def __init__(self):
        # MinIO
        self.minio_client = Minio(
            os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
            secure=False
        )

        # PostgreSQL DWH
        dwh_url = (
            f"postgresql://{os.getenv('DWH_USER', 'dwh_admin')}:"
            f"{os.getenv('DWH_PASSWORD', 'dwh_password')}"
            f"@{os.getenv('DWH_HOST', 'localhost')}:{os.getenv('DWH_PORT', '5433')}"
            f"/{os.getenv('DWH_DATABASE', 'news_warehouse')}"
        )
        self.engine = create_engine(dwh_url)

        self.results = []
        logger.info("✅ Framework de qualité initialisé")

    # ================================================================
    # TESTS BRONZE (Articles bruts)
    # ================================================================

    def test_bronze_files_exist(self):
        """Vérifie qu'il y a des fichiers dans le bucket Bronze."""
        result = DataQualityResult(
            test_name="Bronze : Fichiers présents",
            dimension="complétude",
            layer="bronze"
        )
        objects = list(self.minio_client.list_objects('bronze', recursive=True))
        json_files = [o for o in objects if o.object_name.endswith('.json')]
        
        failed = 0 if len(json_files) > 0 else 1
        result.evaluate(total=1, failed=failed, threshold=1.0)
        result.details = f"{len(json_files)} fichiers JSON trouvés"
        self.results.append(result)
        return result

    def test_bronze_article_has_title(self):
        """Vérifie que chaque article Bronze a un titre non vide."""
        result = DataQualityResult(
            test_name="Bronze : Article a un titre",
            dimension="complétude",
            layer="bronze"
        )
        total, failed = 0, 0
        objects = list(self.minio_client.list_objects('bronze', recursive=True))
        
        for obj in objects:
            if not obj.object_name.endswith('.json'):
                continue
            try:
                response = self.minio_client.get_object('bronze', obj.object_name)
                data = json.loads(response.read().decode('utf-8'))
                response.close()
                response.release_conn()
                
                for article in data.get('articles', []):
                    total += 1
                    title = article.get('title', '')
                    if not title or title == "Sans titre" or title == "No title" or title == "بدون عنوان":
                        failed += 1
            except Exception:
                pass
        
        result.evaluate(total=total, failed=failed, threshold=0.90)
        result.details = f"{total - failed}/{total} articles avec titre valide"
        self.results.append(result)
        return result

    def test_bronze_article_has_content(self):
        """Vérifie que chaque article a du contenu (min 50 caractères)."""
        result = DataQualityResult(
            test_name="Bronze : Article a du contenu (>50 chars)",
            dimension="complétude",
            layer="bronze"
        )
        total, failed = 0, 0
        objects = list(self.minio_client.list_objects('bronze', recursive=True))
        
        for obj in objects:
            if not obj.object_name.endswith('.json'):
                continue
            try:
                response = self.minio_client.get_object('bronze', obj.object_name)
                data = json.loads(response.read().decode('utf-8'))
                response.close()
                response.release_conn()
                
                for article in data.get('articles', []):
                    total += 1
                    content = article.get('content', '') or article.get('description', '')
                    if len(content) < 50:
                        failed += 1
            except Exception:
                pass
        
        result.evaluate(total=total, failed=failed, threshold=0.85)
        result.details = f"{total - failed}/{total} articles avec contenu suffisant"
        self.results.append(result)
        return result

    def test_bronze_article_has_url(self):
        """Vérifie que chaque article a une URL valide."""
        result = DataQualityResult(
            test_name="Bronze : Article a une URL",
            dimension="validité",
            layer="bronze"
        )
        total, failed = 0, 0
        objects = list(self.minio_client.list_objects('bronze', recursive=True))
        
        for obj in objects:
            if not obj.object_name.endswith('.json'):
                continue
            try:
                response = self.minio_client.get_object('bronze', obj.object_name)
                data = json.loads(response.read().decode('utf-8'))
                response.close()
                response.release_conn()
                
                for article in data.get('articles', []):
                    total += 1
                    url = article.get('url', '')
                    if not url or not url.startswith('http'):
                        failed += 1
            except Exception:
                pass
        
        result.evaluate(total=total, failed=failed, threshold=0.95)
        result.details = f"{total - failed}/{total} articles avec URL valide"
        self.results.append(result)
        return result

    # ================================================================
    # TESTS SILVER (Articles enrichis NLP)
    # ================================================================

    def _read_silver_data(self) -> pd.DataFrame:
        """Lit tous les fichiers Parquet du bucket Silver."""
        objects = list(self.minio_client.list_objects('silver', recursive=True))
        parquet_files = [o.object_name for o in objects if o.object_name.endswith('.parquet')]
        
        if not parquet_files:
            return pd.DataFrame()
        
        all_dfs = []
        for pf in parquet_files:
            try:
                response = self.minio_client.get_object('silver', pf)
                df = pd.read_parquet(BytesIO(response.read()))
                response.close()
                response.release_conn()
                all_dfs.append(df)
            except Exception:
                pass
        
        return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

    def test_silver_language_detected(self):
        """Vérifie que la langue est détectée pour chaque article Silver."""
        result = DataQualityResult(
            test_name="Silver : Langue détectée",
            dimension="complétude",
            layer="silver"
        )
        df = self._read_silver_data()
        if df.empty:
            result.evaluate(0, 0)
            result.details = "Aucune donnée Silver"
            self.results.append(result)
            return result
        
        total = len(df)
        failed = len(df[df['language'].isin(['unknown', '', None]) | df['language'].isna()])
        
        result.evaluate(total=total, failed=failed, threshold=0.90)
        result.details = f"{total - failed}/{total} articles avec langue détectée"
        self.results.append(result)
        return result

    def test_silver_keywords_extracted(self):
        """Vérifie que des mots-clés ont été extraits."""
        result = DataQualityResult(
            test_name="Silver : Mots-clés extraits",
            dimension="complétude",
            layer="silver"
        )
        df = self._read_silver_data()
        if df.empty:
            result.evaluate(0, 0)
            result.details = "Aucune donnée Silver"
            self.results.append(result)
            return result
        
        total = len(df)
        failed = len(df[df['keywords_str'].isin(['', None]) | df['keywords_str'].isna()])
        
        result.evaluate(total=total, failed=failed, threshold=0.80)
        result.details = f"{total - failed}/{total} articles avec mots-clés"
        self.results.append(result)
        return result

    def test_silver_sentiment_calculated(self):
        """Vérifie que le sentiment est calculé."""
        result = DataQualityResult(
            test_name="Silver : Sentiment calculé",
            dimension="complétude",
            layer="silver"
        )
        df = self._read_silver_data()
        if df.empty:
            result.evaluate(0, 0)
            self.results.append(result)
            return result
        
        total = len(df)
        failed = len(df[df['sentiment_label'].isin(['', None]) | df['sentiment_label'].isna()])
        
        result.evaluate(total=total, failed=failed, threshold=0.95)
        result.details = f"{total - failed}/{total} articles avec sentiment"
        self.results.append(result)
        return result

    def test_silver_word_count_valid(self):
        """Vérifie que word_count > 20 (articles substantiels)."""
        result = DataQualityResult(
            test_name="Silver : Contenu substantiel (>20 mots)",
            dimension="validité",
            layer="silver"
        )
        df = self._read_silver_data()
        if df.empty:
            result.evaluate(0, 0)
            self.results.append(result)
            return result
        
        total = len(df)
        failed = len(df[df['word_count'] < 20])
        
        result.evaluate(total=total, failed=failed, threshold=0.90)
        result.details = f"{total - failed}/{total} articles avec >20 mots"
        self.results.append(result)
        return result

    def test_silver_no_duplicates(self):
        """Vérifie qu'il n'y a pas de doublons dans Silver."""
        result = DataQualityResult(
            test_name="Silver : Pas de doublons",
            dimension="cohérence",
            layer="silver"
        )
        df = self._read_silver_data()
        if df.empty:
            result.evaluate(0, 0)
            self.results.append(result)
            return result
        
        total = len(df)
        duplicates = total - df['article_id'].nunique()
        
        result.evaluate(total=total, failed=duplicates, threshold=0.90)
        result.details = f"{duplicates} doublons détectés sur {total} articles"
        self.results.append(result)
        return result

    # ================================================================
    # TESTS DWH (Data Warehouse PostgreSQL)
    # ================================================================

    def test_dwh_fact_articles_not_empty(self):
        """Vérifie que fact_articles contient des données."""
        result = DataQualityResult(
            test_name="DWH : fact_articles non vide",
            dimension="complétude",
            layer="dwh"
        )
        try:
            with self.engine.connect() as conn:
                count = conn.execute(text("SELECT COUNT(*) FROM fact_articles")).scalar()
            
            failed = 0 if count > 0 else 1
            result.evaluate(total=1, failed=failed, threshold=1.0)
            result.details = f"{count} articles dans le DWH"
        except Exception as e:
            result.evaluate(0, 1)
            result.details = f"Erreur : {e}"
        
        self.results.append(result)
        return result

    def test_dwh_all_sources_present(self):
        """Vérifie que les 5 sources sont représentées."""
        result = DataQualityResult(
            test_name="DWH : 5 sources représentées",
            dimension="complétude",
            layer="dwh"
        )
        try:
            with self.engine.connect() as conn:
                count = conn.execute(text(
                    "SELECT COUNT(DISTINCT source_id) FROM fact_articles"
                )).scalar()
            
            failed = 0 if count >= 5 else (5 - count)
            result.evaluate(total=5, failed=failed, threshold=1.0)
            result.details = f"{count}/5 sources présentes"
        except Exception as e:
            result.evaluate(0, 1)
            result.details = f"Erreur : {e}"
        
        self.results.append(result)
        return result

    def test_dwh_all_languages_present(self):
        """Vérifie que les 3 langues sont représentées."""
        result = DataQualityResult(
            test_name="DWH : 3 langues (FR/EN/AR)",
            dimension="complétude",
            layer="dwh"
        )
        try:
            with self.engine.connect() as conn:
                count = conn.execute(text(
                    "SELECT COUNT(DISTINCT language_id) FROM fact_articles"
                )).scalar()
            
            failed = 0 if count >= 3 else (3 - count)
            result.evaluate(total=3, failed=failed, threshold=1.0)
            result.details = f"{count}/3 langues présentes"
        except Exception as e:
            result.evaluate(0, 1)
            result.details = f"Erreur : {e}"
        
        self.results.append(result)
        return result

    def test_dwh_referential_integrity(self):
        """Vérifie l'intégrité référentielle (FK valides)."""
        result = DataQualityResult(
            test_name="DWH : Intégrité référentielle",
            dimension="cohérence",
            layer="dwh"
        )
        try:
            with self.engine.connect() as conn:
                orphans = conn.execute(text("""
                    SELECT COUNT(*) FROM fact_articles f
                    WHERE f.source_id NOT IN (SELECT source_id FROM dim_source)
                       OR f.language_id NOT IN (SELECT language_id FROM dim_language)
                       OR f.date_id NOT IN (SELECT date_id FROM dim_date)
                """)).scalar()
                
                total = conn.execute(text("SELECT COUNT(*) FROM fact_articles")).scalar()
            
            result.evaluate(total=total, failed=orphans, threshold=1.0)
            result.details = f"{orphans} enregistrements orphelins sur {total}"
        except Exception as e:
            result.evaluate(0, 1)
            result.details = f"Erreur : {e}"
        
        self.results.append(result)
        return result

    def test_dwh_sentiment_range(self):
        """Vérifie que les scores de sentiment sont entre -1 et +1."""
        result = DataQualityResult(
            test_name="DWH : Sentiment entre -1 et +1",
            dimension="validité",
            layer="dwh"
        )
        try:
            with self.engine.connect() as conn:
                total = conn.execute(text("SELECT COUNT(*) FROM fact_articles")).scalar()
                invalid = conn.execute(text("""
                    SELECT COUNT(*) FROM fact_articles 
                    WHERE sentiment_score < -1 OR sentiment_score > 1
                """)).scalar()
            
            result.evaluate(total=total, failed=invalid, threshold=1.0)
            result.details = f"{invalid} scores hors range sur {total}"
        except Exception as e:
            result.evaluate(0, 1)
            result.details = f"Erreur : {e}"
        
        self.results.append(result)
        return result

    # ================================================================
    # RAPPORT DE QUALITÉ
    # ================================================================

    def generate_report(self) -> pd.DataFrame:
        """Génère un rapport tabulaire de tous les tests."""
        rows = [r.to_dict() for r in self.results]
        df = pd.DataFrame(rows)
        return df

    def print_report(self):
        """Affiche le rapport dans la console."""
        df = self.generate_report()
        
        passed = len([r for r in self.results if r.passed])
        failed = len([r for r in self.results if not r.passed])
        total = len(self.results)
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 RAPPORT DE QUALITÉ DES DONNÉES")
        logger.info(f"   Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        # Par layer
        for layer in ['bronze', 'silver', 'dwh']:
            layer_results = [r for r in self.results if r.layer == layer]
            if not layer_results:
                continue
            
            layer_name = {'bronze': '🥉 BRONZE', 'silver': '🥈 SILVER', 'dwh': '🏛️ DWH'}
            logger.info(f"\n{'─' * 50}")
            logger.info(f"{layer_name.get(layer, layer)}")
            logger.info(f"{'─' * 50}")
            
            for r in layer_results:
                status = "✅" if r.passed else "❌"
                logger.info(
                    f"  {status} {r.test_name:45s} | "
                    f"{r.success_rate:.0%} | {r.details}"
                )
        
        # Résumé global
        logger.info(f"\n{'=' * 70}")
        logger.info(f"📊 RÉSUMÉ : {passed}/{total} tests passés ({passed/total:.0%})")
        
        if failed > 0:
            logger.warning(f"⚠️  {failed} tests échoués :")
            for r in self.results:
                if not r.passed:
                    logger.warning(f"   ❌ {r.test_name} ({r.success_rate:.0%})")
        else:
            logger.success("🎉 TOUS LES TESTS PASSENT !")
        
        logger.info("=" * 70)
        
        return df

    def run_all(self) -> pd.DataFrame:
        """Lance tous les tests et génère le rapport."""
        logger.info("🚀 Démarrage des tests de qualité\n")
        
        # Bronze
        logger.info("🥉 Tests Bronze...")
        self.test_bronze_files_exist()
        self.test_bronze_article_has_title()
        self.test_bronze_article_has_content()
        self.test_bronze_article_has_url()
        
        # Silver
        logger.info("\n🥈 Tests Silver...")
        self.test_silver_language_detected()
        self.test_silver_keywords_extracted()
        self.test_silver_sentiment_calculated()
        self.test_silver_word_count_valid()
        self.test_silver_no_duplicates()
        
        # DWH
        logger.info("\n🏛️ Tests DWH...")
        self.test_dwh_fact_articles_not_empty()
        self.test_dwh_all_sources_present()
        self.test_dwh_all_languages_present()
        self.test_dwh_referential_integrity()
        self.test_dwh_sentiment_range()
        
        # Rapport
        return self.print_report()


if __name__ == "__main__":
    framework = DataQualityFramework()
    report = framework.run_all()