"""
DAG Airflow : Scraping batch des 5 sources de news.
Schedulé toutes les heures.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Configuration commune
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


def scrape_source(source_name: str, **context):
    """Lance un scraper donné. Importé dynamiquement pour éviter les imports lourds au parse."""
    import sys
    import os
    sys.path.insert(0, '/opt/airflow')
    
    # Override env vars pour le conteneur Airflow
    # (services accessibles par nom de conteneur, pas localhost)
    os.environ['MINIO_ENDPOINT'] = 'minio:9000'
    os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
    os.environ['MINIO_SECRET_KEY'] = 'minioadmin'
    os.environ['BUCKET_BRONZE'] = 'bronze'
    os.environ['BUCKET_SILVER'] = 'silver'
    os.environ['BUCKET_GOLD'] = 'gold'
    
    scrapers_map = {
        'hespress': 'scrapers.hespress_scraper.HespressScraper',
        'bbc': 'scrapers.bbc_scraper.BBCScraper',
        'akhbarona': 'scrapers.akhbarona_scraper.AkhbaronaScraper',
        'aljazeera': 'scrapers.aljazeera_scraper.AlJazeeraScraper',
        'franceinfo': 'scrapers.franceinfo_scraper.FranceInfoScraper',
    }
    
    if source_name not in scrapers_map:
        raise ValueError(f"Source inconnue : {source_name}")
    
    # Import dynamique
    module_path, class_name = scrapers_map[source_name].rsplit('.', 1)
    module = __import__(module_path, fromlist=[class_name])
    ScraperClass = getattr(module, class_name)
    
    # Exécution
    scraper = ScraperClass()
    stats = scraper.run(max_articles=15, delay=1.5)
    
    print(f"✅ {source_name} : {stats}")
    return stats


with DAG(
    dag_id='dag_batch_scraping',
    description='Scraping batch des 5 sources de news (Bronze layer)',
    default_args=default_args,
    start_date=datetime(2026, 5, 6),
    schedule_interval='@hourly',  # Toutes les heures
    catchup=False,
    tags=['news', 'scraping', 'bronze', 'batch'],
) as dag:

    # Une tâche par source (parallélisable)
    scrape_hespress = PythonOperator(
        task_id='scrape_hespress',
        python_callable=scrape_source,
        op_kwargs={'source_name': 'hespress'},
    )

    scrape_bbc = PythonOperator(
        task_id='scrape_bbc',
        python_callable=scrape_source,
        op_kwargs={'source_name': 'bbc'},
    )

    scrape_akhbarona = PythonOperator(
        task_id='scrape_akhbarona',
        python_callable=scrape_source,
        op_kwargs={'source_name': 'akhbarona'},
    )

    scrape_aljazeera = PythonOperator(
        task_id='scrape_aljazeera',
        python_callable=scrape_source,
        op_kwargs={'source_name': 'aljazeera'},
    )

    scrape_franceinfo = PythonOperator(
        task_id='scrape_franceinfo',
        python_callable=scrape_source,
        op_kwargs={'source_name': 'franceinfo'},
    )

    # Toutes les tâches s'exécutent en PARALLÈLE
    # (pas de dépendances entre elles)