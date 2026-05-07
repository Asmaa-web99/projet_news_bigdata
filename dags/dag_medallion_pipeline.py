"""
DAG Airflow : Pipeline Médaillon Bronze → Silver → Gold.
Schedulé toutes les 2 heures.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator


default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}


def run_bronze_to_silver(**context):
    """Lance le pipeline Bronze → Silver."""
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
    
    from medallion.bronze_to_silver import BronzeToSilverPipeline
    pipeline = BronzeToSilverPipeline()
    pipeline.run()
    return "Bronze → Silver OK"


def run_silver_to_gold(**context):
    """Lance le pipeline Silver → Gold."""
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
    
    from medallion.silver_to_gold import SilverToGoldPipeline
    pipeline = SilverToGoldPipeline()
    pipeline.run()
    return "Silver → Gold OK"


with DAG(
    dag_id='dag_medallion_pipeline',
    description='Pipeline Médaillon : Bronze → Silver → Gold',
    default_args=default_args,
    start_date=datetime(2026, 5, 6),
    schedule_interval=timedelta(hours=2),  # Toutes les 2 heures
    catchup=False,
    tags=['news', 'medallion', 'transformation'],
) as dag:

    bronze_to_silver = PythonOperator(
        task_id='bronze_to_silver',
        python_callable=run_bronze_to_silver,
    )

    silver_to_gold = PythonOperator(
        task_id='silver_to_gold',
        python_callable=run_silver_to_gold,
    )

    # Bronze → Silver DOIT terminer avant Silver → Gold
    bronze_to_silver >> silver_to_gold