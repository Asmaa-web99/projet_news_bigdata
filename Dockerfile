# Dockerfile - Apache Airflow 2.7.1 + Python dependencies
# Utilisé pour construire l'image Docker du pipeline orchestration

FROM apache/airflow:2.7.1-python3.10

USER root

# Installer les dépendances système (git, build tools, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow

# Copier le fichier requirements.txt et installer uniquement les dépendances métier.
# Airflow est déjà fourni par l'image de base.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copier la structure du projet dans le conteneur
COPY --chown=airflow:root dags /opt/airflow/dags
COPY --chown=airflow:root scrapers /opt/airflow/scrapers
COPY --chown=airflow:root medallion /opt/airflow/medallion
COPY --chown=airflow:root warehouse /opt/airflow/warehouse
COPY --chown=airflow:root quality /opt/airflow/quality
COPY --chown=airflow:root data /opt/airflow/data

# Vérifier que tout est bien copié
RUN ls -la /opt/airflow/dags && echo "✅ Dockerfile build completed"
