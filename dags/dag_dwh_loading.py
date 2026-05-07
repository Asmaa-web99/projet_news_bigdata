"""
DAG Airflow : Chargement Gold → Data Warehouse PostgreSQL.
Schedulé 1 fois par jour à 02h00.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator


default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def run_dwh_loading(**context):
    """Charge les tables Gold dans PostgreSQL DWH."""
    import sys
    import os
    sys.path.insert(0, '/opt/airflow')
    
    # Override env vars pour le conteneur
    os.environ['MINIO_ENDPOINT'] = 'minio:9000'
    os.environ['MINIO_ACCESS_KEY'] = 'minioadmin'
    os.environ['MINIO_SECRET_KEY'] = 'minioadmin'
    os.environ['BUCKET_BRONZE'] = 'bronze'
    os.environ['BUCKET_SILVER'] = 'silver'
    os.environ['BUCKET_GOLD'] = 'gold'
    os.environ['DWH_HOST'] = 'postgres_dwh'
    os.environ['DWH_PORT'] = '5432'
    os.environ['DWH_DATABASE'] = 'news_warehouse'
    os.environ['DWH_USER'] = 'dwh_admin'
    os.environ['DWH_PASSWORD'] = 'dwh_password'
    
    from warehouse.load_to_dwh import GoldToDWHLoader
    loader = GoldToDWHLoader()
    loader.run()
    return "DWH chargé"


with DAG(
    dag_id='dag_dwh_loading',
    description='Chargement Gold → Data Warehouse',
    default_args=default_args,
    start_date=datetime(2026, 5, 6),
    schedule_interval='0 2 * * *',  # 02h00 chaque jour
    catchup=False,
    tags=['news', 'dwh', 'postgresql'],
) as dag:

    load_to_dwh = PythonOperator(
        task_id='load_gold_to_dwh',
        python_callable=run_dwh_loading,
    )