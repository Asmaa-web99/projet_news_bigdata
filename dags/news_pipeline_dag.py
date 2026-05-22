"""
=====================================================================
DAG UNIFIÉ: Pipeline Big Data d'Analyse de Médias
=====================================================================
Orchestration complète :
  1. Scraping batch des 5 sources de news → Bronze (MinIO)
  2. Transformation Bronze → Silver (NLP, nettoyage)
  3. Transformation Silver → Gold (agrégation, KPIs)
  4. Chargement Gold → Data Warehouse PostgreSQL
  5. Contrôles qualité des données
  6. Préparation pour Metabase

Schedule : Toutes les heures (batch scraping)
DAG ID : news_bigdata_pipeline
Timeout : 3 heures max par DAG run
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
import logging

# Logger
log = logging.getLogger(__name__)

# =====================================================================
# CONFIGURATION DES VARIABLES
# =====================================================================

default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag_config = {
    'max_articles_per_source': 20,
    'scraping_delay': 1.5,
    'bronze_to_silver_batch_size': 100,
    'quality_check_threshold': 0.95,
}

# =====================================================================
# FONCTIONS PYTHON POUR LES TÂCHES
# =====================================================================

def setup_environment(**context):
    """
    Initialise les variables d'environnement pour le conteneur Docker.
    Les services communiquent via les noms de conteneur, pas localhost.
    """
    import os
    
    log.info("🔧 Initialisation de l'environnement Docker...")
    
    os.environ['MINIO_ENDPOINT'] = 'minio:9000'
    os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
    os.environ['MINIO_SECRET_KEY'] = 'minioadmin'
    os.environ['BUCKET_BRONZE'] = 'bronze'
    os.environ['BUCKET_SILVER'] = 'silver'
    os.environ['BUCKET_GOLD'] = 'gold'
    os.environ['KAFKA_BOOTSTRAP_SERVERS'] = 'kafka:9092'
    os.environ['DWH_HOST'] = 'postgres_dwh'
    os.environ['DWH_PORT'] = '5432'
    os.environ['DWH_DATABASE'] = 'news_warehouse'
    os.environ['DWH_USER'] = 'dwh_admin'
    os.environ['DWH_PASSWORD'] = 'dwh_password'
    
    log.info("✅ Variables d'environnement configurées")
    return "Environment setup complete"


def scrape_source(source_name: str, **context):
    """
    Lance le scraper pour une source donnée.
    Résultat : articles stockés en JSON dans MinIO Bronze.
    
    Args:
        source_name: 'hespress', 'bbc', 'akhbarona', 'aljazeera', ou 'franceinfo'
    """
    import sys
    import os
    sys.path.insert(0, '/opt/airflow')
    
    # Re-initialiser les variables d'environnement
    os.environ['MINIO_ENDPOINT'] = 'minio:9000'
    os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
    os.environ['MINIO_SECRET_KEY'] = 'minioadmin'
    os.environ['BUCKET_BRONZE'] = 'bronze'
    
    log.info(f"🔄 Scraping : {source_name.upper()}")
    
    # Mapping des scrapers
    scrapers_map = {
        'hespress': 'scrapers.hespress_scraper.HespressScraper',
        'bbc': 'scrapers.bbc_scraper.BBCScraper',
        'akhbarona': 'scrapers.akhbarona_scraper.AkhbaronaScraper',
        'aljazeera': 'scrapers.aljazeera_scraper.AlJazeeraScraper',
        'franceinfo': 'scrapers.franceinfo_scraper.FranceInfoScraper',
    }
    
    if source_name not in scrapers_map:
        raise ValueError(f"❌ Source inconnue : {source_name}")
    
    try:
        # Import dynamique du scraper
        module_path, class_name = scrapers_map[source_name].rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        ScraperClass = getattr(module, class_name)
        
        # Exécution
        scraper = ScraperClass()
        stats = scraper.run(
            max_articles=dag_config['max_articles_per_source'],
            delay=dag_config['scraping_delay']
        )
        
        log.info(f"✅ {source_name} : {stats}")
        return {
            'source': source_name,
            'status': 'success',
            'stats': stats
        }
    except Exception as e:
        log.error(f"❌ Erreur {source_name} : {str(e)}")
        return {
            'source': source_name,
            'status': 'error',
            'error': str(e)
        }


def run_bronze_to_silver(**context):
    """
    Pipeline Bronze → Silver
    Lit les articles bruts (Bronze), applique nettoyage + NLP, 
    sauvegarde en Parquet (Silver).
    """
    import sys
    import os
    sys.path.insert(0, '/opt/airflow')
    
    # Env vars
    os.environ['MINIO_ENDPOINT'] = 'minio:9000'
    os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
    os.environ['MINIO_SECRET_KEY'] = 'minioadmin'
    os.environ['BUCKET_BRONZE'] = 'bronze'
    os.environ['BUCKET_SILVER'] = 'silver'
    
    log.info("🔄 Pipeline Bronze → Silver")
    
    try:
        from medallion.bronze_to_silver import BronzeToSilverPipeline
        
        pipeline = BronzeToSilverPipeline()
        result = pipeline.run()
        
        log.info(f"✅ Bronze → Silver terminé : {result}")
        return result
    except Exception as e:
        log.error(f"❌ Erreur Bronze → Silver : {str(e)}")
        raise


def run_silver_to_gold(**context):
    """
    Pipeline Silver → Gold
    Lit les articles transformés (Silver), applique agrégations et KPIs,
    sauvegarde résultat (Gold).
    """
    import sys
    import os
    sys.path.insert(0, '/opt/airflow')
    
    # Env vars
    os.environ['MINIO_ENDPOINT'] = 'minio:9000'
    os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
    os.environ['MINIO_SECRET_KEY'] = 'minioadmin'
    os.environ['BUCKET_SILVER'] = 'silver'
    os.environ['BUCKET_GOLD'] = 'gold'
    
    log.info("🔄 Pipeline Silver → Gold")
    
    try:
        from medallion.silver_to_gold import SilverToGoldPipeline
        
        pipeline = SilverToGoldPipeline()
        result = pipeline.run()
        
        log.info(f"✅ Silver → Gold terminé : {result}")
        return result
    except Exception as e:
        log.error(f"❌ Erreur Silver → Gold : {str(e)}")
        raise


def load_gold_to_dwh(**context):
    """
    Chargement final Gold → Data Warehouse PostgreSQL
    Insère les articles Gold dans les tables Star Schema du DWH.
    """
    import sys
    import os
    sys.path.insert(0, '/opt/airflow')
    
    # Env vars
    os.environ['MINIO_ENDPOINT'] = 'minio:9000'
    os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
    os.environ['MINIO_SECRET_KEY'] = 'minioadmin'
    os.environ['BUCKET_GOLD'] = 'gold'
    os.environ['DWH_HOST'] = 'postgres_dwh'
    os.environ['DWH_PORT'] = '5432'
    os.environ['DWH_DATABASE'] = 'news_warehouse'
    os.environ['DWH_USER'] = 'dwh_admin'
    os.environ['DWH_PASSWORD'] = 'dwh_password'
    
    log.info("🔄 Chargement Gold → Data Warehouse")
    
    try:
        from warehouse.load_to_dwh import GoldToDWHLoader
        
        loader = GoldToDWHLoader()
        result = loader.run()
        
        log.info(f"✅ Chargement DWH terminé : {result}")
        return result
    except Exception as e:
        log.error(f"❌ Erreur chargement DWH : {str(e)}")
        raise


def run_quality_checks(**context):
    """
    Contrôles qualité des données (Great Expectations style)
    Teste : Complétude, Cohérence, Validité, Fraîcheur
    """
    import sys
    import os
    sys.path.insert(0, '/opt/airflow')
    
    # Env vars
    os.environ['MINIO_ENDPOINT'] = 'minio:9000'
    os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
    os.environ['MINIO_SECRET_KEY'] = 'minioadmin'
    os.environ['DWH_HOST'] = 'postgres_dwh'
    os.environ['DWH_PORT'] = '5432'
    os.environ['DWH_DATABASE'] = 'news_warehouse'
    os.environ['DWH_USER'] = 'dwh_admin'
    os.environ['DWH_PASSWORD'] = 'dwh_password'
    
    log.info("🔄 Contrôles qualité des données")
    
    try:
        from quality.data_quality_checks import DataQualityFramework
        
        dq_framework = DataQualityFramework()
        results = dq_framework.run_all()
        
        # Afficher résumé
        log.info(f"✅ Contrôles qualité terminés")
        log.info(f"📊 Résumé : {results}")
        
        return results
    except Exception as e:
        log.error(f"❌ Erreur contrôles qualité : {str(e)}")
        # Ne pas lever l'exception pour ne pas bloquer le pipeline
        return {'status': 'error', 'message': str(e)}


def prepare_metabase(**context):
    """
    Tâche finale : préparation données pour Metabase
    Crée views pour tableaux de bord si nécessaire.
    """
    import sys
    import os
    sys.path.insert(0, '/opt/airflow')
    
    # Env vars
    os.environ['DWH_HOST'] = 'postgres_dwh'
    os.environ['DWH_PORT'] = '5432'
    os.environ['DWH_DATABASE'] = 'news_warehouse'
    os.environ['DWH_USER'] = 'dwh_admin'
    os.environ['DWH_PASSWORD'] = 'dwh_password'
    
    log.info("🔄 Préparation données pour Metabase")
    
    try:
        from sqlalchemy import create_engine, text
        
        dwh_url = (
            f"postgresql://dwh_admin:dwh_password"
            f"@postgres_dwh:5432/news_warehouse"
        )
        engine = create_engine(dwh_url)
        
        with engine.connect() as conn:
            # Vérifier que les tables existent
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'"
            )).scalar()
            log.info(f"✅ {result} tables trouvées dans le DWH")
        
        return f"Metabase preparation complete - {result} tables available"
    except Exception as e:
        log.error(f"❌ Erreur préparation Metabase : {str(e)}")
        return {'status': 'warning', 'message': str(e)}


# =====================================================================
# DÉFINITION DU DAG
# =====================================================================

with DAG(
    dag_id='news_bigdata_pipeline',
    description=(
        'Pipeline Big Data unifié : '
        'Scraping batch → Bronze → Silver → Gold → DWH → Qualité → Metabase'
    ),
    default_args=default_args,
    start_date=datetime(2026, 5, 6),
    schedule_interval='@hourly',  # Toutes les heures
    catchup=False,
    tags=['news', 'scraping', 'medallion', 'dwh', 'production'],
    max_active_runs=2,
    doc_md=__doc__,
) as dag:

    # =====================================================================
    # TÂCHE 0 : Initialisation
    # =====================================================================
    
    init_env = PythonOperator(
        task_id='setup_environment',
        python_callable=setup_environment,
        provide_context=True,
        queue='default',
    )

    # =====================================================================
    # TÂCHE 1 : Scraping Batch (5 sources en parallèle)
    # =====================================================================

    scrape_hespress = PythonOperator(
        task_id='scrape_hespress',
        python_callable=scrape_source,
        op_kwargs={'source_name': 'hespress'},
        provide_context=True,
    )

    scrape_bbc = PythonOperator(
        task_id='scrape_bbc',
        python_callable=scrape_source,
        op_kwargs={'source_name': 'bbc'},
        provide_context=True,
    )

    scrape_akhbarona = PythonOperator(
        task_id='scrape_akhbarona',
        python_callable=scrape_source,
        op_kwargs={'source_name': 'akhbarona'},
        provide_context=True,
    )

    scrape_aljazeera = PythonOperator(
        task_id='scrape_aljazeera',
        python_callable=scrape_source,
        op_kwargs={'source_name': 'aljazeera'},
        provide_context=True,
    )

    scrape_franceinfo = PythonOperator(
        task_id='scrape_franceinfo',
        python_callable=scrape_source,
        op_kwargs={'source_name': 'franceinfo'},
        provide_context=True,
    )

    # =====================================================================
    # TÂCHE 2 : Bronze → Silver
    # =====================================================================

    bronze_to_silver = PythonOperator(
        task_id='bronze_to_silver_transformation',
        python_callable=run_bronze_to_silver,
        provide_context=True,
        trigger_rule=TriggerRule.ALL_DONE,
    )

    # =====================================================================
    # TÂCHE 3 : Silver → Gold
    # =====================================================================

    silver_to_gold = PythonOperator(
        task_id='silver_to_gold_transformation',
        python_callable=run_silver_to_gold,
        provide_context=True,
    )

    # =====================================================================
    # TÂCHE 4 : Gold → DWH PostgreSQL
    # =====================================================================

    load_to_dwh = PythonOperator(
        task_id='load_gold_to_dwh',
        python_callable=load_gold_to_dwh,
        provide_context=True,
    )

    # =====================================================================
    # TÂCHE 5 : Contrôles qualité
    # =====================================================================

    quality_checks = PythonOperator(
        task_id='data_quality_checks',
        python_callable=run_quality_checks,
        provide_context=True,
        trigger_rule=TriggerRule.ALL_DONE,
    )

    # =====================================================================
    # TÂCHE 6 : Préparation Metabase
    # =====================================================================

    metabase_prep = PythonOperator(
        task_id='prepare_metabase_dashboard',
        python_callable=prepare_metabase,
        provide_context=True,
        trigger_rule=TriggerRule.ALL_DONE,
    )

    # =====================================================================
    # DÉFINITION DES DÉPENDANCES
    # =====================================================================

    # Étape 0 : Initialisation
    init_env

    # Étape 1 : Scraping en parallèle (dépend de init_env)
    init_env >> [
        scrape_hespress,
        scrape_bbc,
        scrape_akhbarona,
        scrape_aljazeera,
        scrape_franceinfo
    ]

    # Étape 2 : Bronze → Silver (attendre tous les scrapers)
    [scrape_hespress, scrape_bbc, scrape_akhbarona, scrape_aljazeera, scrape_franceinfo] >> bronze_to_silver

    # Étape 3 : Silver → Gold
    bronze_to_silver >> silver_to_gold

    # Étape 4 : Gold → DWH
    silver_to_gold >> load_to_dwh

    # Étape 5 et 6 : Qualité et Metabase (parallèles, après DWH)
    load_to_dwh >> [quality_checks, metabase_prep]


if __name__ == "__main__":
    dag
