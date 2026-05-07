# 📰 Plateforme Big Data d'Analyse de Médias

Une plateforme complète de Big Data pour collecter, transformer et analyser en temps réel les articles de presse de sources multiples.

## 🎯 Problématique

Comment construire une plateforme Big Data capable de collecter, transformer et analyser les articles de presse pour identifier les tendances d'actualité, comparer la couverture médiatique entre sources et détecter les sujets émergents ?

---

## 🏗️ Architecture Globale

```
SOURCES (5 sites) → INGESTION (Batch + Streaming) → DATA LAKE (MinIO)
   ↓
TRANSFORMATIONS (Médaillon) → WAREHOUSE (PostgreSQL) → DASHBOARD (Streamlit)
   ↓
ORCHESTRATION (Airflow) | QUALITÉ (Great Expectations)
```

---

## 📊 Métriques du Projet

| Métrique               | Valeur                           |
| ---------------------- | -------------------------------- |
| **Articles batch**     | 104                              |
| **Articles streaming** | 95                               |
| **Mots indexés**       | 53,071                           |
| **Sources**            | 5 (FR/EN/AR)                     |
| **Pays couverts**      | 4                                |
| **Langues**            | 3 (FR 41.3%, EN 38.5%, AR 20.2%) |

---

## 🛠️ Stack Technique

### Infrastructure

- **MinIO** - Data Lake S3-compatible
- **Kafka + Zookeeper** - Streaming temps réel
- **PostgreSQL** - Data Warehouse
- **Airflow** - Orchestration
- **Metabase** - Visualisation pro
- **Streamlit** - Dashboard interactif

### Python

- **Scraping:** `BeautifulSoup`, `requests`
- **Streaming:** `kafka-python-ng`, `feedparser`
- **NLP:** `langdetect`, `scikit-learn`, lexiques custom
- **Data:** `pandas`, `pyarrow`, `numpy`
- **DWH:** `sqlalchemy`, `psycopg2-binary`

---

## 📂 Structure du Projet

```
projet_news_bigdata/
├── docker-compose.yml          # 7 services
├── requirements.txt            # Dépendances
├── scrapers/                   # Sources Batch (5 scrapers)
├── streaming/                  # Ingestion Kafka
├── medallion/                  # Transformations (Bronze/Silver/Gold)
├── warehouse/                  # Data Warehouse (Star Schema)
├── dags/                       # Orchestration Airflow (3 DAGs)
├── dashboards/                 # Visualisation Streamlit
├── quality/                    # Tests Great Expectations
└── docs/                       # Documentation
```

---

## 🚀 Démarrage Rapide

### Prérequis

- Docker & Docker Compose
- Python 3.9+
- PostgreSQL (optionnel si utilisé via Docker)

### Installation

```bash
# 1. Cloner le repository
git clone https://github.com/Asmaa-web99/projet_news_bigdata.git
cd projet_news_bigdata

# 2. Démarrer les services
docker-compose up -d

# 3. Vérifier que tout est up
docker-compose ps
```

### Utilisation

#### Pipeline Batch Complet

```bash
# Scraping
python -m scrapers.hespress_scraper
python -m scrapers.bbc_scraper
# ... autres scrapers

# Transformations Médaillon
python medallion/bronze_to_silver.py
python medallion/silver_to_gold.py

# Charger le DWH
python warehouse/load_to_dwh.py
```

#### Streaming Kafka

```bash
# Terminal 1: Producer RSS
python streaming/rss_producer.py

# Terminal 2: Consumer
python streaming/kafka_to_bronze_consumer.py
```

#### Dashboard

```bash
streamlit run dashboards/streamlit_app.py
```

#### Airflow

```bash
# Accéder à http://localhost:8080
# Default: airflow / airflow
```

---

## 🎯 Composants Clés

### 1️⃣ Web Scraping

- **5 sources** : Hespress (FR), BBC (EN), Akhbarona (AR), Al Jazeera (EN), France Info (FR)
- **BeautifulSoup** + **Requests** pour parsing
- **Retry automatique** avec backoff exponentiel
- **Déduplication** via MD5 hash
- **Logs persistés** (loguru)

### 2️⃣ Architecture Médaillon

- **Bronze** : JSON brut de sources
- **Silver** : Nettoyage + NLP (langue, mots-clés, sentiment)
- **Gold** : 8 tables analytiques prêtes pour BI

### 3️⃣ NLP Multilingue

- Détection langue (langdetect)
- TF-IDF extraction mots-clés
- **Sentiment Analysis** (lexiques custom FR/EN/AR)
- 57.7% articles négatifs détectés

### 4️⃣ Data Warehouse

- Star Schema (4 tables : dimensions + faits)
- 30+ colonnes pour analyse
- Intégration PostgreSQL

### 5️⃣ Orchestration Airflow

- **DAG 1** : Scraping batch (@hourly, 5 parallèles)
- **DAG 2** : Médaillon pipeline (2h, Bronze→Silver→Gold)
- **DAG 3** : Chargement DWH (quotidien 02h UTC)

### 6️⃣ Dashboard Streamlit

- 8+ visualisations interactives
- 5 KPIs en haut
- Filtres dynamiques (sources/langues)
- Section sentiment détaillée
- Top 20 mots-clés tendance

---

## 🔍 Insights Découverts

- **57.7%** des articles sont **NÉGATIFS** 🔴
- **27.9%** neutres ⚪
- **14.4%** positifs 🟢
- Sources avec sentiment le plus négatif : Akhbarona (-0.8)
- Tendances : Iran, Hantavirus dominent l'actualité

---

## 🌐 Interfaces Web

| Service   | URL                   | Credentials             |
| --------- | --------------------- | ----------------------- |
| MinIO     | http://localhost:9001 | minioadmin / minioadmin |
| Airflow   | http://localhost:8080 | airflow / airflow       |
| Metabase  | http://localhost:3000 | (config initiale)       |
| Streamlit | http://localhost:8501 | -                       |

---

## ✅ Conformité Cahier des Charges

- ✅ Web scraping (5 sources)
- ✅ Architecture distribuée (Docker)
- ✅ Data Lake (MinIO)
- ✅ Médaillon (Bronze/Silver/Gold)
- ✅ Batch & Streaming (Airflow + Kafka)
- ✅ Data Warehouse (PostgreSQL Star Schema)
- ✅ Visualisation (Streamlit + Metabase)
- ✅ Qualité données (Great Expectations)
- ✅ Gouvernance (logs + documentation)

**Couverture : 100%**

---

## 🎓 Compétences Techniques Démontrées

- Architecture Lambda (Batch + Speed)
- Architecture Médaillon (dimensional modeling)
- Stream Processing (Kafka)
- NLP multilingue
- Orchestration de pipelines complexes
- Containerisation Docker
- Data Warehouse design
- Code modulaire & DRY principles

---

## 📚 Documentation

- [Architecture détaillée](./docs/)
- [Schéma Base de Données](./warehouse/schema.sql)
- [Configuration Docker](./docker-compose.yml)
- [Requirements Python](./requirements.txt)

---

## 🔧 Troubleshooting

**Kafka ne démarre pas:**

```bash
docker-compose down -v
docker-compose up -d
```

**MinIO inaccessible:**

```bash
docker exec news_minio minio server /minio_data
```

**Airflow manque les dépendances:**

```bash
docker exec -u airflow news_airflow python -m pip install --user -r /tmp/requirements.txt
```

---

## 📝 License

Projet académique - Tous droits réservés.

---

**Dernière mise à jour:** Mai 2026
