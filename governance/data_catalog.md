# 📰 NEWS BIG DATA PLATFORM - Architecture & Gouvernance des Données

**Version:** 1.0  
**Dernière mise à jour:** Mai 2026  
**Statut:** Production-Ready

---

## 📋 TABLE DES MATIÈRES

1. [Dictionnaire de Données](#dictionnaire-de-données)
2. [Architecture Médaillon](#architecture-médaillon)
3. [Data Warehouse](#data-warehouse)
4. [Règles de Qualité](#règles-de-qualité)
5. [Traçabilité & Gouvernance](#traçabilité--gouvernance)
6. [SLAs & Métriques](#slas--métriques)

---

## 📊 DICTIONNAIRE DE DONNÉES

### Champs Collectés par Scraper

Chaque article collecté contient les champs suivants :

| Champ              | Type      | Source         | Nullable | Description                              |
| ------------------ | --------- | -------------- | -------- | ---------------------------------------- |
| `title`            | STRING    | Source web     | Non      | Titre de l'article                       |
| `author`           | STRING    | Source web     | Oui      | Nom de l'auteur                          |
| `content`          | TEXT      | Source web     | Non      | Corps/contenu principal                  |
| `summary`          | TEXT      | Source web     | Oui      | Résumé ou sous-titre                     |
| `publication_date` | TIMESTAMP | Source web     | Non      | Date/heure de publication                |
| `category`         | STRING    | Source web     | Oui      | Catégorie (politique, tech, sport, etc.) |
| `url`              | STRING    | Source web     | Non      | URL unique de l'article                  |
| `source`           | STRING    | Config scraper | Non      | Nom de la source (hespress, bbc, etc.)   |
| `language`         | STRING    | Config scraper | Non      | Code langue ISO 639-1 (fr, en, ar)       |
| `country`          | STRING    | Config scraper | Non      | Code pays ISO 3166-1 (MA, GB, EG, etc.)  |
| `scraped_at`       | TIMESTAMP | Pipeline       | Non      | Timestamp du scraping                    |

### Métadonnées Ajoutées par Couche

#### Bronze (Couche Brute)

- `source_file` : Path MinIO du fichier JSON source
- `ingestion_timestamp` : Moment de l'ingestion en Bronze
- `ingestion_id` : UUID unique de l'ingestion

#### Silver (Couche Transformée)

- `language_detected` : Langue détectée via NLP (peut différer de `language`)
- `language_confidence` : Score de confiance (0-1)
- `is_valid` : Boolean - article respecte les critères de validité
- `word_count` : Nombre de mots après nettoyage
- `keyword_list` : Liste de mots-clés extrait (JSON)
- `sentiment_score` : Score de sentiment (-1 à 1)
- `sentiment_label` : Catégorie (POSITIVE, NEUTRAL, NEGATIVE)
- `transformed_at` : Timestamp de transformation Bronze → Silver

#### Gold (Couche Agrégée)

- `article_id` : UUID unique pour le DWH
- `is_duplicate` : Boolean - détecté comme doublon URL
- `duplicate_group_id` : UUID si doublon d'un autre article
- `source_id` : FK vers dim_source
- `language_id` : FK vers dim_language
- `category_id` : FK vers dim_category (si créée)
- `aggregation_date` : Date d'agrégation
- `processed_at` : Timestamp final de transformation Silver → Gold

---

## 🏗️ ARCHITECTURE MÉDAILLON

### Bronze Layer 📦 (MinIO)

**Responsabilité :** Ingestion brute sans transformation

**Format :** JSON line-delimited  
**Location MinIO :** `s3://bronze/`  
**Partition :** Par source et date  
**Rétention :** 30 jours

**Contenu :** Données exactes telles que scrapées

```json
{
  "title": "Breaking News Title",
  "author": "John Doe",
  "content": "<html>Article content...</html>",
  "publication_date": "2026-05-09T14:30:00Z",
  "category": "politics",
  "url": "https://example.com/article-123",
  "source": "hespress",
  "language": "fr",
  "country": "MA",
  "scraped_at": "2026-05-09T14:35:00Z"
}
```

**Fichier exemple :**

```
bronze/
├── hespress/
│   └── 2026-05-09/
│       └── hespress_2026-05-09_14-35.json
├── bbc/
│   └── 2026-05-09/
│       └── bbc_2026-05-09_14-35.json
└── ...
```

### Silver Layer 🔧 (MinIO)

**Responsabilité :** Nettoyage, validation, enrichissement NLP

**Format :** Apache Parquet (compressé)  
**Location MinIO :** `s3://silver/`  
**Partition :** Par date (YYYY/MM/DD)  
**Rétention :** 90 jours

**Transformations appliquées :**

1. ✨ Nettoyage HTML : suppression des balises, décodage entities
2. 🔤 Détection de langue automatique (langdetect)
3. ✅ Validation : titre non vide, contenu > 20 mots, URL non vide
4. 🔑 Extraction de mots-clés (TF-IDF ou YAKE)
5. 😊 Analyse de sentiment (textblob ou transformers)
6. 📊 Statistiques texte : word_count, char_count, reading_time

**Schéma Parquet :**

```
StructType([
  StructField('title', StringType()),
  StructField('author', StringType()),
  StructField('content', StringType()),
  StructField('publication_date', TimestampType()),
  StructField('category', StringType()),
  StructField('url', StringType()),
  StructField('source', StringType()),
  StructField('language', StringType()),
  StructField('language_detected', StringType()),
  StructField('language_confidence', DoubleType()),
  StructField('is_valid', BooleanType()),
  StructField('word_count', IntegerType()),
  StructField('keyword_list', ArrayType(StringType())),
  StructField('sentiment_score', DoubleType()),
  StructField('sentiment_label', StringType()),
  StructField('transformed_at', TimestampType()),
])
```

**Fichier exemple :**

```
silver/
├── 2026/05/09/
│   ├── articles_2026-05-09_00.parquet
│   ├── articles_2026-05-09_01.parquet
│   └── articles_2026-05-09_02.parquet
└── ...
```

### Gold Layer 🏆 (MinIO)

**Responsabilité :** Agrégation, KPIs, préparation pour DWH

**Format :** Apache Parquet (optimisé pour requêtes analytiques)  
**Location MinIO :** `s3://gold/`  
**Partition :** Par date  
**Rétention :** 1 an (archivé ensuite)

**Transformations appliquées :**

1. 🔄 Déduplication par URL + source
2. 📐 Agrégations temporelles : tendances horaires, daily summaries
3. 🎯 KPIs : sentiment moyen par source, top keywords, top articles
4. 🌍 Agrégations géographiques et par langue
5. 📈 Calcul de métriques : engagement estimé, viralité potentielle
6. 🔗 Jointure avec dimensions (source, language, category)

**Schéma Final (prêt pour DWH) :**

```
StructType([
  StructField('article_id', StringType()),  # UUID
  StructField('title', StringType()),
  StructField('author', StringType()),
  StructField('content', StringType()),
  StructField('publication_date', TimestampType()),
  StructField('category', StringType()),
  StructField('url', StringType()),
  StructField('source', StringType()),
  StructField('source_id', IntegerType()),  # FK
  StructField('language', StringType()),
  StructField('language_id', IntegerType()),  # FK
  StructField('word_count', IntegerType()),
  StructField('keyword_list', ArrayType(StringType())),
  StructField('sentiment_score', DoubleType()),
  StructField('sentiment_label', StringType()),
  StructField('is_duplicate', BooleanType()),
  StructField('duplicate_group_id', StringType()),
  StructField('scraped_at', TimestampType()),
  StructField('processed_at', TimestampType()),
])
```

---

## 💾 DATA WAREHOUSE (PostgreSQL)

### Architecture Star Schema

```
        ┌─────────────────┐
        │   FACT_ARTICLE  │
        │   (Central)     │
        └─────────────────┘
              │  │  │  │
    ┌─────────┘  │  │  └──────────┐
    │            │  │             │
    ▼            ▼  ▼             ▼
┌──────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│dim_source│ │dim_date│ │dim_lang  │ │dim_categ │
└──────────┘ └────────┘ └──────────┘ └──────────┘
```

### Tables de Dimension

#### `dim_source` - Sources d'articles

```sql
CREATE TABLE dim_source (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(50) UNIQUE NOT NULL,  -- hespress, bbc, etc.
    base_url VARCHAR(500),
    language VARCHAR(5),
    country VARCHAR(5),
    scraper_type VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `dim_language` - Langues détectées

```sql
CREATE TABLE dim_language (
    language_id SERIAL PRIMARY KEY,
    language_code VARCHAR(5) UNIQUE NOT NULL,  -- fr, en, ar
    language_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `dim_date` - Dates complètes (pour agrégations rapides)

```sql
CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    date_value DATE UNIQUE NOT NULL,
    year INT,
    month INT,
    day INT,
    day_of_week VARCHAR(10),
    quarter INT,
    is_weekend BOOLEAN
);
```

#### `dim_category` (Optionnel)

```sql
CREATE TABLE dim_category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    parent_category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Table de Faits

#### `fact_article` - Articles enrichis

```sql
CREATE TABLE fact_article (
    article_id UUID PRIMARY KEY,
    source_id INT NOT NULL REFERENCES dim_source,
    date_id INT NOT NULL REFERENCES dim_date,
    language_id INT REFERENCES dim_language,

    title VARCHAR(500) NOT NULL,
    author VARCHAR(200),
    content TEXT,
    url VARCHAR(1000) UNIQUE NOT NULL,
    category VARCHAR(100),

    publication_timestamp TIMESTAMP,
    word_count INT,
    keyword_list TEXT[],  -- PostgreSQL array

    sentiment_score FLOAT,
    sentiment_label VARCHAR(20),

    is_duplicate BOOLEAN DEFAULT false,
    duplicate_group_id UUID,

    scraped_at TIMESTAMP NOT NULL,
    processed_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT valid_sentiment CHECK (sentiment_score BETWEEN -1 AND 1)
);

CREATE INDEX idx_fact_article_source ON fact_article(source_id);
CREATE INDEX idx_fact_article_date ON fact_article(date_id);
CREATE INDEX idx_fact_article_language ON fact_article(language_id);
CREATE INDEX idx_fact_article_url ON fact_article(url);
```

### Vues Analytiques (pour Metabase)

#### `v_daily_sentiment` - Sentiment par jour

```sql
CREATE VIEW v_daily_sentiment AS
SELECT
    d.date_value,
    s.source_name,
    l.language_name,
    COUNT(*) as article_count,
    AVG(fa.sentiment_score) as avg_sentiment,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fa.sentiment_score) as median_sentiment,
    SUM(CASE WHEN fa.sentiment_label = 'POSITIVE' THEN 1 ELSE 0 END) as positive_count,
    SUM(CASE WHEN fa.sentiment_label = 'NEUTRAL' THEN 1 ELSE 0 END) as neutral_count,
    SUM(CASE WHEN fa.sentiment_label = 'NEGATIVE' THEN 1 ELSE 0 END) as negative_count
FROM fact_article fa
JOIN dim_date d ON fa.date_id = d.date_id
JOIN dim_source s ON fa.source_id = s.source_id
LEFT JOIN dim_language l ON fa.language_id = l.language_id
GROUP BY d.date_value, s.source_name, l.language_name
ORDER BY d.date_value DESC;
```

#### `v_trending_keywords` - Mots-clés tendances

```sql
CREATE VIEW v_trending_keywords AS
SELECT
    unnest(keyword_list) as keyword,
    COUNT(*) as frequency,
    d.date_value,
    s.source_name
FROM fact_article fa
JOIN dim_date d ON fa.date_id = d.date_id
JOIN dim_source s ON fa.source_id = s.source_id
WHERE fa.keyword_list IS NOT NULL
    AND fa.processed_at > NOW() - INTERVAL '7 days'
GROUP BY keyword, d.date_value, s.source_name
ORDER BY frequency DESC;
```

---

## ✅ RÈGLES DE QUALITÉ

### Tests de Complétude

| Couche | Test              | Seuil | Dimension  |
| ------ | ----------------- | ----- | ---------- |
| Bronze | URL non vide      | 100%  | Validité   |
| Bronze | Titre non vide    | 100%  | Validité   |
| Silver | Content non NULL  | 95%   | Complétude |
| Silver | Sentiment assigné | 95%   | Complétude |
| Gold   | article_id unique | 100%  | Intégrité  |

### Tests de Validité

| Couche | Test                | Règle                   |
| ------ | ------------------- | ----------------------- |
| Bronze | URL format valide   | Commence par http(s):// |
| Bronze | Date parseable      | Format ISO 8601         |
| Silver | Langage détecté     | Code ISO 639-1 valide   |
| Silver | Sentiment score     | Entre -1 et 1           |
| Gold   | Pas doublon par URL | Une URL = un article    |

### Tests de Cohérence

| Test                 | Règle                                          |
| -------------------- | ---------------------------------------------- |
| Source cohérente     | Bronze.source = Gold.source_id                 |
| Langue cohérente     | Silver.language_detected consistent            |
| Dates chronologiques | publication_date <= scraped_at <= processed_at |
| Intégrité FK         | Toutes les FKs pointent vers dims              |

### Tests de Fraîcheur

| Métrique             | Seuil    | Alerte   |
| -------------------- | -------- | -------- |
| Délai ingestion      | < 5 min  | > 10 min |
| Délai transformation | < 10 min | > 20 min |
| Délai chargement DWH | < 5 min  | > 10 min |
| Articles reçus/heure | > 10     | < 5      |

---

## 🔐 TRAÇABILITÉ & GOUVERNANCE

### Lineage des Données

```
Source Web (Hespress, BBC, etc.)
         ↓
    BRONZE (MinIO)
    [Données brutes JSON]
         ↓
  SILVER (MinIO)
  [Nettoyage HTML, Validation, NLP]
         ↓
   GOLD (MinIO)
   [Déduplication, Agrégations, KPIs]
         ↓
   DWH PostgreSQL
   [Star Schema - Fact + Dimensions]
         ↓
   Metabase
   [Dashboards et Rapports]
```

### Métadonnées de Traçabilité

Chaque article porte :

- `scraped_at` : Moment exact du scraping
- `source` : Source d'origine
- `processed_at` : Moment de la dernière transformation
- `article_id` : Identifiant unique UUID généré en Gold

### Gouvernance des Accès

| Rôle          | Accès Airflow  | Accès MinIO | Accès DWH    | Accès Metabase |
| ------------- | -------------- | ----------- | ------------ | -------------- |
| Admin         | Full           | Full        | Full         | Full           |
| Data Engineer | DAG creation   | Buckets R/W | Schema DDL   | All            |
| Data Analyst  | DAG monitoring | Buckets R   | Query SELECT | All reports    |
| Business User | -              | -           | -            | Dashboards R   |

### Conformité Données

- ✅ RGPD : Pas de données personnelles sensibles (pas de numéro sécu, etc.)
- ✅ Traçabilité complète : Chaque article a son lineage documenté
- ✅ Rétention : Bronze 30j, Silver 90j, Gold 1an
- ✅ Audit : Tous les chargements enregistrés en `loaded_at`

---

## 📊 SLAs & MÉTRIQUES

### SLAs Opérationnels

| Composant                | SLA   | Métrique                            |
| ------------------------ | ----- | ----------------------------------- |
| Scraping                 | 99.5% | Articles collectés/heure            |
| Ingestion Bronze         | 95%   | Articles en Bronze < 5 min          |
| Transformation Medallion | 98%   | Silver/Gold < 10 min après Bronze   |
| Chargement DWH           | 99%   | Articles en DWH < 20 min après Gold |
| Qualité données          | > 95% | Taux de réussite tests qualité      |

### Métriques Clés

**Volume:**

- Articles/jour par source
- Total articles en warehouse
- Croissance cumulative

**Qualité:**

- % articles valides (Bronze)
- % articles sans doublon (Gold)
- % tests qualité passants

**Performance:**

- Temps de transformation moyen
- Taille fichiers Parquet
- Nombre de requêtes Metabase

---

## 🔄 CHANGELOG & VERSIONING

### Version 1.0 (Mai 2026)

- ✅ 5 sources de scraping (Hespress, BBC, Akhbarona, Al Jazeera, France Info)
- ✅ Pipeline Médaillon complet (Bronze → Silver → Gold)
- ✅ Star Schema DWH
- ✅ Dashboards Metabase
- ✅ Contrôles qualité automatisés
- ✅ Orchestration Airflow

### Versions Futures

- [ ] Streaming Kafka intégré (vs. batch actuellement)
- [ ] ML models : classification de catégories, NER
- [ ] Data archival : déplacement vers S3/Cloud après 1 an
- [ ] Multi-language support amélioré (17+ langues)
- [ ] Real-time alerting sur anomalies

---

**Document rédigé pour usage interne Data Engineering  
Merci de mettre à jour ce document à chaque évolution majeure du pipeline.**
