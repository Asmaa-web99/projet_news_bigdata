# 📅 PLAN D'ACTION GRANULAIRE - DU 7 AU 10 MAI 2026

## 🎯 OBJECTIF FINAL

Soumettre avant 10 mai 23:59 UTC:

- ✅ Code source complet (PRÊT)
- ✅ Environnement Docker (PRÊT)
- ❌ Rapport PDF (À FAIRE)
- ❌ Présentation PPT (À FAIRE)
- ❌ Documentation Gouvernance (À FAIRE)

**Temps total requis:** 30 heures réparties sur 3-4 jours

---

## 📆 JOUR 1 - MARDI 7 MAI 2026 (8h-20h = 12h)

### ⏰ 08:00 - 09:00 | Setup Environnement (1h)

**Objectif:** Préparer outils et fichiers

```powershell
# 1. Créer dossier de travail
mkdir C:\Users\hp\Desktop\LIVRABLE_FINAL

# 2. Vérifier Docker
docker-compose --version      # Doit être 2.20+
docker ps                      # Vérifier containers actifs

# 3. Ouvrir éditeurs
# - Microsoft Word (rapport)
# - Microsoft PowerPoint (présentation)
# - VS Code (docs markdown)
# - Chrome (inspiration + recherches)

# 4. Créer structure
mkdir docs/
touch docs/DATA_CATALOG.md
touch docs/DATA_LINEAGE.md
touch docs/GOVERNANCE_FRAMEWORK.md
```

**Livrables de phase:** Environnement prêt, dossiers créés

---

### ⏰ 09:00 - 10:30 | Recherche & Références (1.5h)

**Objectif:** Collecter 15+ références pour rapport

**Tâches:**

```
[ ] Architecture Médaillon (Databricks white paper)
[ ] MinIO documentation S3-compatible
[ ] Airflow best practices
[ ] Star Schema (Kimball)
[ ] NLP multilingue (langdetect, TF-IDF)
[ ] PostgreSQL vs NoSQL
[ ] Web scraping ethics
[ ] Great Expectations
[ ] Docker Compose best practices
[ ] Data governance frameworks
```

**Outils:** Google Scholar, medium.com, dev.to, docs officiels

**Livrables de phase:** Fichier references.txt avec 15+ liens

---

### ⏰ 10:30 - 14:00 | RAPPORT - PARTIE 1 (3.5h)

**Objectif:** Écrire chapitres 1-4 (Intro + État art + Specs + Architecture)

#### Structure à suivre:

```
1. INTRODUCTION (0.5h)
   ├─ Contexte: Big Data, media analytics
   ├─ Enjeux: Tendances, sentiment, fake news
   ├─ Objectifs: Architecture complète, 5 sources
   ├─ Scope: 104 articles batch, 3 langues
   └─ Word count: ~300 mots

2. ÉTAT DE L'ART (1h)
   ├─ Web Scraping:
   │  ├─ BeautifulSoup (léger, flexible)
   │  ├─ Scrapy (lourd, scalable)
   │  └─ Justif: BeautifulSoup suffisant pour 5 sources
   ├─ Architecture Médaillon (Databricks)
   ├─ ETL vs ELT
   ├─ Data Warehouse (Kimball)
   └─ NLP (langdetect, TF-IDF, sentiment)
   Refs: 3-4 sources clés

3. PROBLÉMATIQUE (1h)
   ├─ Cahier des charges 10 points
   ├─ Modèle conceptuel (données → insight)
   ├─ Contraintes:
   │  ├─ Tempo: Real-time (streaming)
   │  ├─ Qualité: SLA 95%+
   │  └─ Scalabilité: +5 sources futur
   └─ Diagramme: Cas d'usage

4. ARCHITECTURE (1h)
   ├─ Vue d'ensemble (7 services Docker)
   ├─ Flux de données
   ├─ Technos choisies + justification
   ├─ Diagramme C4 niveau 1
   └─ Tableau: Services + ports + images
```

**Dossier de travail:** `RAPPORT_V1.docx` créé localement

**Livrables de phase:** 4 chapitres brouillon, ~2000 mots

---

### ⏰ 14:00 - 15:30 | Pause + Déjeuner (1.5h)

**Récupération mentale et physique → Important pour productivité**

---

### ⏰ 15:30 - 19:00 | RAPPORT - PARTIE 2 (3.5h)

**Objectif:** Écrire chapitres 5-7 (Implémentation détaillée)

```
5. IMPLÉMENTATION (2h)
   ├─ 1️⃣ SOURCES: Scrapers BeautifulSoup
   │  ├─ Hespress (FR/MA)
   │  ├─ BBC (EN/UK)
   │  ├─ Akhbarona (AR/MA)
   │  ├─ Al Jazeera (EN/QA)
   │  └─ France Info (FR/FR)
   │  Code sample: __init__ + scrape()
   │
   ├─ 2️⃣ INGESTION: Batch + Streaming
   │  ├─ Batch: @hourly via Airflow
   │  ├─ Streaming: RSS → Kafka
   │  ├─ Topic config: 3 partitions
   │  └─ Diagram: Source flow
   │
   ├─ 3️⃣ DATA LAKE: MinIO
   │  ├─ 3 buckets: bronze/silver/gold
   │  ├─ Structure: source/YYYY/MM/DD/
   │  ├─ Formats: JSON → Parquet
   │  └─ Capacité: ~1GB/mois
   │
   ├─ 4️⃣ MEDALLION: Transformations
   │  ├─ Bronze (raw): Articles JSON bruts
   │  ├─ Silver (clean):
   │  │  ├─ HTML cleanup
   │  │  ├─ Langage detection
   │  │  ├─ Validation (>20 mots)
   │  │  └─ Enrichissement NLP
   │  ├─ Gold (analytics):
   │  │  ├─ 8 tables pré-agrégées
   │  │  ├─ TF-IDF keywords
   │  │  └─ Sentiment scores
   │  └─ Code: nlp_utils.py details
   │
   ├─ 5️⃣ WAREHOUSE: Star Schema PostgreSQL
   │  ├─ Dimensions: source/language/date
   │  ├─ Fact: fact_articles (30+ cols)
   │  ├─ Schéma: Diagramme ERD
   │  └─ Intégrité: FK constraints
   │
   ├─ 6️⃣ DASHBOARD: Streamlit
   │  ├─ KPIs (5)
   │  ├─ Visualisations (8+)
   │  ├─ Filtres (source, langue)
   │  └─ Screenshots: 3-4 images
   │
   ├─ 7️⃣ ORCHESTRATION: Airflow 3 DAGs
   │  ├─ dag_batch_scraping (@hourly)
   │  ├─ dag_medallion_pipeline (2h)
   │  ├─ dag_dwh_loading (02:00 UTC)
   │  └─ Code snippets: Key functions
   │
   ├─ 8️⃣ QUALITÉ: Great Expectations
   │  ├─ 4 dimensions (complétude, etc)
   │  ├─ Tests Bronze/Silver/Gold/DWH
   │  └─ SLA: 95% success rate
   │
   └─ 9️⃣ GOUVERNANCE: Logs + Lineage
      ├─ loguru rotatif (7 jours)
      ├─ Data lineage (source→DWH)
      └─ Audit trail (timestamps)

6. RÉSULTATS (1h)
   ├─ Métriques clés
   │  ├─ 104 articles scraped (batch)
   │  ├─ 95 articles streaming
   │  ├─ 53,071 mots indexés
   │  ├─ 5 sources, 4 pays
   │  ├─ 3 langues (FR 41.3%, EN 38.5%, AR 20.2%)
   │  └─ 41 catégories
   │
   ├─ Couverture géographique
   │  └─ Tableau: Pays x Volume
   │
   ├─ Sentiment Analysis
   │  ├─ Négatif: 57.7%
   │  ├─ Neutre: 27.9%
   │  ├─ Positif: 14.4%
   │  └─ Graphique camembert + par source
   │
   └─ Tendances découvertes
      └─ Iran, Hantavirus, Détroit d'Ormuz

7. TESTS & VALIDATION (0.5h)
   ├─ Tests unitaires (5 fichiers)
   ├─ Tests intégration (pipeline complet)
   ├─ Great Expectations results
   └─ Performance (< 10s Silver→Gold)
```

**Livrables de phase:** Chapters 5-7 complets, ~3000 mots, 3-4 code samples

---

### ⏰ 19:00 - 20:00 | Finition JOUR 1 (1h)

**Tâches:**

```
[ ] Relire chapitres 1-7 (orthographe)
[ ] Ajouter images/diagrammes (Mermaid PNG export)
[ ] Créer 1ère table des matières
[ ] Sauvegarder RAPPORT_V1.pdf backup
```

**Livrables de jour:** RAPPORT_V1 avec 7 chapitres, ~6000 mots

**Temps total jour 1:** 12 heures ✅

---

## 📆 JOUR 2 - MERCREDI 8 MAI 2026 (8h-20h = 12h)

### ⏰ 08:00 - 10:00 | RAPPORT - PARTIE 3 (2h)

**Objectif:** Chapitres 8-10 + Annexes

```
8. LIMITATIONS & PERSPECTIVES (0.5h)
   ├─ Limitations:
   │  ├─ Batch 1h (temps réel limité)
   │  ├─ 5 sources seulement
   │  ├─ Langage français/anglais/arabe
   │  └─ Sentiment lexique simple
   │
   └─ Améliorations futures:
      ├─ Apache Spark (scalabilité)
      ├─ ML avancé (recommandations)
      ├─ More languages
      └─ Real-time scoring

9. CONCLUSION (0.5h)
   ├─ Bilan du projet
   ├─ Résultats atteints (100% cahier charges)
   ├─ Apprentissages clés
   └─ Impact futur

10. RÉFÉRENCES (0.5h)
    ├─ 15+ sources bibliographiques
    ├─ Format: APA ou Harvard
    └─ Liens + DOI
```

**Livrables de phase:** Chapitres 8-10, ~1500 mots

---

### ⏰ 10:00 - 11:30 | RAPPORT - ANNEXES (1.5h)

**Objectif:** Créer annexes A-E

```
ANNEXE A: Configuration Docker (0.3h)
├─ docker-compose.yml complet
└─ .env template

ANNEXE B: Schéma Base de Données (0.3h)
├─ Diagramme ERD complet (Mermaid)
├─ SQL CREATE TABLE
└─ Indexes et contraintes

ANNEXE C: Code Samples (0.5h)
├─ base_scraper.py (30 lignes clés)
├─ nlp_utils.py (20 lignes)
├─ silver_to_gold.py (15 lignes)
└─ dashboard snippet (10 lignes)

ANNEXE D: Logs d'Exécution (0.2h)
├─ Premier scraping log (success)
├─ DAG exécution Airflow
└─ Airflow task logs

ANNEXE E: Screenshots (0.2h)
├─ MinIO console
├─ Airflow DAG graph
├─ Dashboard Streamlit (3-4)
└─ PostgreSQL tables
```

**Livrables de phase:** 5 annexes structurées

---

### ⏰ 11:30 - 13:00 | Finition RAPPORT (1.5h)

**Tâches:**

```
[ ] Relecture complète (orthographe + grammar)
[ ] Vérifier numérotation chapitres
[ ] Créer table des matières finale (auto)
[ ] Ajouter page de garde + signatures
[ ] Ajouter en-têtes/pieds de page
[ ] Export PDF final + validation
[ ] Backup version Word
```

**Format final:**

- PDF A4, police 11pt, interligne 1.5
- 25-30 pages
- Header/Footer avec numéro page
- Pagination automatique

**Livrables de phase:** RAPPORT_FINAL.pdf complet et validé

---

### ⏰ 13:00 - 14:30 | Pause Déjeuner (1.5h)

---

### ⏰ 14:30 - 18:00 | PRÉSENTATION PPT (3.5h)

**Objectif:** 30 slides prêtes pour soutenance

#### Structuration par bloc (adapté de RAPPORT):

```
BLOC 1: OUVERTURE (1 slide)
└─ Slide 1: Couverture
   ├─ Titre: "Plateforme Big Data d'Analyse de Médias"
   ├─ Sous-titre: Architecture Distribuée pour News Analytics
   ├─ Auteurs: Noms binôme
   ├─ Encadrant: Pr. Lamia KARIM
   ├─ Date: 8 mai 2026
   └─ Logo université

BLOC 2: CONTEXTE (2 slides)
├─ Slide 2: Problématique
│  ├─ "Comment analyser les tendances médiatiques?"
│  ├─ 1000s articles/jour
│  ├─ Multi-sources, multi-langues
│  ├─ Sentiment analysis required
│  └─ Image: Newspapers montage
│
└─ Slide 3: Objectifs
   ├─ Collecter 5 sources
   ├─ Ingestion batch + streaming
   ├─ Architecture Médaillon
   └─ Dashboard analytics

BLOC 3: ARCHITECTURE (2 slides)
├─ Slide 4: Vue Globale (Diagramme)
│  └─ Sources → Ingestion → Lake → Transform → DWH → Dashboard
│
└─ Slide 5: Stack Technique
   └─ Tableau: Component | Technology | Port

BLOC 4: SOURCES (2 slides)
├─ Slide 6: 5 Scrapers
│  └─ Tableau: Source | Pays | Langue | URL Pattern
│
└─ Slide 7: BeautifulSoup Details
   ├─ Parsing HTML
   ├─ Retry + Déduplication
   └─ Code snippet (5 lignes)

BLOC 5: INGESTION (2 slides)
├─ Slide 8: Batch Ingestion
│  └─ Airflow @hourly, 5 parallèles
│
└─ Slide 9: Streaming Ingestion
   └─ Kafka RSS → Bronze

BLOC 6: DATA LAKE (2 slides)
├─ Slide 10: MinIO Overview
│  └─ S3-compatible, 3 buckets
│
└─ Slide 11: Structure
   └─ Bronze/Silver/Gold paths

BLOC 7: TRANSFORMATIONS (3 slides)
├─ Slide 12: Bronze → Silver
│  ├─ HTML cleanup
│  ├─ Language detection
│  └─ NLP enrichment
│
├─ Slide 13: NLP Details
│  ├─ langdetect (FR/EN/AR)
│  ├─ TF-IDF keywords
│  └─ Sentiment analysis
│
└─ Slide 14: Silver → Gold
   └─ 8 tables analytiques

BLOC 8: WAREHOUSE (2 slides)
├─ Slide 15: Star Schema
│  └─ Diagramme ERD complet
│
└─ Slide 16: Fact Table
   └─ 30+ colonnes détail

BLOC 9: ORCHESTRATION (1 slide)
└─ Slide 17: 3 DAGs Airflow
   └─ Graphiques avec dépendances

BLOC 10: DASHBOARD (1 slide)
└─ Slide 18: Streamlit
   └─ 3-4 screenshots

BLOC 11: QUALITÉ (1 slide)
└─ Slide 19: Great Expectations
   └─ 4 dimensions testées

BLOC 12: RÉSULTATS (2 slides)
├─ Slide 20: Métriques Clés
│  ├─ 104 articles batch
│  ├─ 53K mots indexés
│  └─ Tableau: Source x Volume
│
└─ Slide 21: Sentiment Analysis
   ├─ 57.7% négatif
   ├─ Graphique par source
   └─ Top tendances

BLOC 13: DÉPLOIEMENT (1 slide)
└─ Slide 22: Docker
   ├─ docker-compose.yml
   ├─ 7 services
   └─ Reproductibilité

BLOC 14: FUTUR (1 slide)
└─ Slide 23: Scalabilité + ML
   ├─ Spark migration
   ├─ Recommandation
   └─ Advanced NLP

BLOC 15: CONCLUSION (1 slide)
└─ Slide 24: Bilan
   ├─ 100% cahier charges
   ├─ Architecture production
   └─ Apprentissages clés

BLOC 16: Q&A (1 slide)
└─ Slide 25: Merci! Questions?

BONUS SLIDES (optionnel):
├─ Slide 26: Bugs résolus (8)
├─ Slide 27: Améliorations futures
└─ Slide 28: Demo live (si vidéo)
```

**Design Guidelines:**

- Couleur principale: Bleu #0066CC
- Police titre: Arial/Helvetica 32pt bold
- Police corps: Arial 18pt
- Images: Min 300 DPI
- Diagrammes: Mermaid + Lucidchart
- Max 5 bullet points/slide

**Livrables de phase:** 25-30 slides complètes

---

### ⏰ 18:00 - 20:00 | Finition PPT + Setup JOUR 3 (2h)

**Tâches PPT:**

```
[ ] Relire contenu (typos)
[ ] Vérifier transitions
[ ] Ajouter animations basiques
[ ] Préparer speaker notes (1 sentence/slide)
[ ] Export PDF backup (en cas panne)
[ ] Tester projection (16:9)
```

**Tâches Docs:**

```
[ ] Créer 3 fichiers gouvernance:
    [ ] DATA_CATALOG.md
    [ ] DATA_LINEAGE.md
    [ ] GOVERNANCE_FRAMEWORK.md
[ ] Adapter contenu RECAP.md
[ ] Ajouter tableaux + listes
```

**Livrables de jour:** PPT final + 3 doc gubernance brouillon

**Temps total jour 2:** 12 heures ✅

---

## 📆 JOUR 3 - JEUDI 9 MAI 2026 (8h-22h = 14h)

### ⏰ 08:00 - 12:00 | Finalisation Gouvernance (4h)

**Objectif:** 3 fichiers docs complétés + polis

#### [docs/DATA_CATALOG.md](docs/DATA_CATALOG.md) (1.5h)

```markdown
# Data Catalog

## 🔵 Bronze Layer (Raw Data)

### Hespress (hespress_scraper.py)

- **Source:** https://www.hespress.com
- **Language:** French (FR)
- **Country:** Morocco (MA)
- **Scraping Frequency:** Hourly (@hourly)
- **Storage Path:** `bronze/hespress/YYYY/MM/DD/hespress_TIMESTAMP.json`
- **File Format:** JSON
- **Partition:** By day
- **Fields:**
  - `article_id` (string): MD5(title + source)
  - `title` (string): Article headline
  - `author` (string): Journalist name (optional)
  - `category` (string): Article category
  - `url` (string): Article link
  - `content` (string): Full article text
  - `publication_date` (datetime): Original publish date
  - `scraping_date` (datetime): When scraped
  - `source` (string): "hespress"
- **Volume:** ~15 articles/day
- **SLA:** ≥ 95% completeness
- **Owner:** Data Team

[Repeat for BBC, Akhbarona, Al Jazeera, France Info]

## 🟡 Silver Layer (Cleaned & Enriched)

### articles_cleaned (bronze_to_silver.py)

- **Path:** `silver/articles/YYYY/MM/DD/articles_TIMESTAMP.parquet`
- **Format:** Apache Parquet (columnar, compressed)
- **Partitioning:** By date (YYYY/MM/DD)
- **Row Count:** ~200 articles daily
- **Columns Added:**
  - `clean_content` (string): HTML removed, normalized
  - `language` (string): Detected language (fr/en/ar/unknown)
  - `keywords` (array<string>): Top 10 TF-IDF keywords
  - `sentiment_score` (float): -1 to +1
  - `sentiment_label` (string): negative/neutral/positive
  - `word_count` (int): # words in content
  - `char_count` (int): # characters
  - `sentence_count` (int): # sentences
- **Transformation Logic:**
  - HTML cleanup: regex remove <\*>
  - Language detect: langdetect.detect(content[:500])
  - Validation: word_count >= 20
  - Keywords: TF-IDF with stopwords
  - Sentiment: Custom lexicon (FR/EN/AR)
- **Quality Threshold:** ≥ 95% valid records

## 🟢 Gold Layer (Analytics)

### Table 1: articles_by_source

- **Purpose:** Articles count per source
- **Path:** `gold/articles_by_source/TIMESTAMP.parquet`
- **Columns:**
  - `source_name` (string): PK
  - `article_count` (int): Total articles
  - `avg_word_count` (float): Average words per article
  - `sentiment_avg` (float): Average sentiment
- **Grain:** 1 row per source
- **Refresh:** Daily

[Repeat for 7 other gold tables]

## 📦 DWH Star Schema (PostgreSQL)

### Fact Table: fact_articles

- **Database:** news_warehouse
- **Connection:** postgres://dwh_admin@localhost:5433
- **Row Count:** 199+ articles
- **Columns:** 30+
- **Key Columns:**
  - `article_id` (varchar): Primary Key
  - `source_id` (int): FK to dim_source
  - `date_id` (int): FK to dim_date
  - `language_id` (int): FK to dim_language
  - `title`, `author`, `category`, `content` (text)
  - `word_count`, `char_count`, `sentence_count` (int)
  - `sentiment_score`, `sentiment_label` (numeric/varchar)
  - `keywords_str` (text): JSON array as string
  - `url`, `publication_date`, `scraping_date` (text/datetime)
- **Indexes:**
  - PK: article_id
  - FK: source_id, date_id, language_id
  - Additional: source_id, publication_date

### Dimension: dim_source

- **Rows:** 5
- **Columns:** source_id, source_name, country, base_url
- **Grain:** 1 row per news source

[Repeat for dim_language, dim_date]

## 📊 Data Dictionary

| Table         | Column     | Type        | Nullable | Description               |
| ------------- | ---------- | ----------- | -------- | ------------------------- |
| fact_articles | article_id | varchar(64) | NO       | Unique article identifier |
| fact_articles | title      | text        | YES      | Article headline          |
| ...           | ...        | ...         | ...      | ...                       |

## 🔍 Data Quality Metrics

| Layer  | Field           | Rule               | Threshold |
| ------ | --------------- | ------------------ | --------- |
| Bronze | title           | NOT NULL           | ≥ 95%     |
| Bronze | content         | Length > 100 chars | ≥ 95%     |
| Silver | language        | IN (fr, en, ar)    | ≥ 98%     |
| Silver | sentiment_score | BETWEEN -1 AND 1   | ≥ 100%    |
| Gold   | source_id       | FK reference       | ≥ 100%    |
| DWH    | article_id      | Unique             | ≥ 100%    |
```

#### [docs/DATA_LINEAGE.md](docs/DATA_LINEAGE.md) (1.5h)

```markdown
# Data Lineage & Traceability

## Overview

Complete data flow from external sources to analytics dashboard.

## Source-to-Storage Lineage
```

External Sources
↓
├─ hespress.com → [hespress_scraper.py]
│ └─ MinIO: bronze/hespress/2026/05/08/hespress*\*.json
│
├─ bbc.com → [bbc_scraper.py]
│ └─ MinIO: bronze/bbc/2026/05/08/bbc*_.json
│
├─ akhbarona.com → [akhbarona_scraper.py]
│ └─ MinIO: bronze/akhbarona/2026/05/08/akhbarona\__.json
│
├─ aljazeera.com → [aljazeera_scraper.py]
│ └─ MinIO: bronze/aljazeera/2026/05/08/aljazeera*\*.json
│
└─ franceinfo.fr → [franceinfo_scraper.py]
└─ MinIO: bronze/franceinfo/2026/05/08/franceinfo*\*.json

    └─ RSS Feeds → [rss_producer.py] → Kafka topic: news_streaming
       └─ [kafka_to_bronze_consumer.py] → MinIO: bronze/streaming/...

```

## Transformation Lineage

```

1. Bronze → Silver Pipeline (2h delay)
   ├─ Input: JSON files from bronze/
   ├─ Processing: [bronze_to_silver.py]
   │ ├─ clean_html(content)
   │ ├─ detect_language(content)
   │ ├─ validate_article(>20 words)
   │ ├─ extract_keywords(TF-IDF)
   │ ├─ analyze_sentiment(lexicon)
   │ └─ compute_stats(text)
   ├─ Output: Parquet files
   └─ MinIO: silver/articles/YYYY/MM/DD/

2. Silver → Gold Pipeline (2h delay)
   ├─ Input: Parquet from silver/
   ├─ Processing: [silver_to_gold.py]
   │ ├─ Deduplicate by article_id
   │ ├─ Create 8 aggregate tables
   │ ├─ group_by(source, language, country, category)
   │ ├─ compute(count, avg_sentiment, keywords)
   │ └─ Export Parquet
   ├─ Output: 8 Parquet files
   └─ MinIO: gold/[table_name]/TIMESTAMP.parquet

3. Gold → DWH Pipeline (daily 02:00 UTC)
   ├─ Input: 8 Parquet files from gold/
   ├─ Processing: [load_to_dwh.py]
   │ ├─ Read gold tables
   │ ├─ Map to dimensions
   │ ├─ UPSERT fact*articles
   │ └─ Validate referential integrity
   ├─ Output: PostgreSQL tables
   └─ PostgreSQL: fact_articles, dim*\*

4. DWH → Dashboard
   ├─ Input: PostgreSQL queries
   ├─ Processing: [streamlit_app.py]
   │ ├─ Query fact_articles
   │ ├─ Join with dimensions
   │ ├─ Aggregate (group by source, language)
   │ ├─ Create visualizations (Plotly)
   │ └─ Apply filters (source, language)
   └─ Output: Web Dashboard (http://localhost:8501)

```

## Orchestration: Airflow DAGs

```

Schedule Timeline:

Every Hour:
├─ 00:00 → dag_batch_scraping (30 min)
│ Scrape 5 sources in parallel
│
├─ 00:30 → dag_medallion_pipeline
│ Bronze → Silver → Gold (2h)
│
└─ Daily 02:00 UTC → dag_dwh_loading
Gold → DWH (1h)

```

## Data Ownership & Stewardship

| Component | Owner | Responsibility |
|-----------|-------|-----------------|
| Sources | Each news site | Availability |
| Bronze Layer | Data Team | Scraping, dedup, storage |
| Silver Layer | Data Team | Cleaning, validation, NLP |
| Gold Layer | Analytics Team | Aggregations, reporting |
| DWH | DWH Team | Schema, referential integrity |
| Dashboard | BI Team | Visualization, user support |

## Traceability Example

```

Example Article Trace:

1. Original: BBC News article published
   └─ URL: https://bbc.com/news/world-...
   └─ Time: 2026-05-08 14:32:00 UTC

2. Bronze Stage:
   └─ File: bronze/bbc/2026/05/08/bbc_2026050814.json
   └─ JSON: { "title": "...", "content": "..." }
   └─ Timestamp: 2026-05-08 14:45:00 (scraped)
   └─ article_id: md5(title + "bbc")

3. Silver Stage:
   └─ File: silver/articles/2026/05/08/articles_cleaned.parquet
   └─ Fields Added:
   ├─ language: "en"
   ├─ keywords: ["uk", "world", ...]
   ├─ sentiment_score: -0.3
   └─ word_count: 487

4. Gold Stage:
   └─ Reflected in 8 tables:
   ├─ articles_by_source (BBC count++)
   ├─ articles_by_language (EN count++)
   ├─ articles_by_country (UK count++)
   └─ top_keywords (updated)

5. DWH Stage:
   └─ fact_articles.article_id = md5(...)
   └─ fact_articles.source_id = 2 (BBC)
   └─ fact_articles.language_id = 1 (EN)
   └─ fact_articles.date_id = 18460 (2026-05-08)

6. Dashboard:
   └─ Visible in:
   ├─ "Articles par source" (BBC +1)
   ├─ "Distribution par langue" (EN +1)
   ├─ "Sentiment par source" (BBC avg updated)
   └─ "Top keywords" (updated rankings)

```

## Change Management

| Change | Date | Reason | Impact |
|--------|------|--------|--------|
| Added Al Jazeera source | 2026-05-06 | Expand coverage | Bronze bucket growth |
| Improved sentiment lexicon | 2026-05-07 | Better accuracy | Gold sentiment refresh |
| Added word_count stat | 2026-05-06 | Readability analysis | Silver + Gold update |
```

#### [docs/GOVERNANCE_FRAMEWORK.md](docs/GOVERNANCE_FRAMEWORK.md) (1h)

```markdown
# Data Governance Framework

## Executive Summary

Comprehensive governance covering data ownership, quality, security, audit,
and retention across all pipeline layers (Bronze → Silver → Gold → DWH).

## Data Ownership & Accountability

### Organizational Structure
```

Chief Data Officer (CDO)
├─ Data Owner: Pr. Lamia KARIM
│ └─ Data Steward: Master IADATA students
│ ├─ Bronze Steward: Ingestion team
│ ├─ Silver Steward: Transformation team
│ ├─ Gold Steward: Analytics team
│ └─ DWH Steward: Warehouse team
│
└─ Technical Owner: DevOps/Data Engineering
├─ Airflow Administrator
├─ MinIO Administrator
└─ PostgreSQL DBA

````

### Responsibilities

| Role | Responsibility |
|------|-----------------|
| Data Owner | Strategic decisions, business value, compliance |
| Data Steward | Data quality, metadata, usage policies |
| Technical Owner | System availability, performance, security |

## Data Quality Management

### Quality Dimensions

1. **Complétude (Completeness)**
   - Definition: % required fields present
   - Threshold: ≥ 95%
   - Bronze: title, content, source NOT NULL
   - Silver: All of Bronze + language, sentiment
   - Gold: All required columns present
   - DWH: referential integrity 100%

2. **Cohérence (Consistency)**
   - Definition: Data conforms to format rules
   - Threshold: ≥ 98%
   - Checks:
     - Date format: YYYY-MM-DD
     - Language IN ['fr', 'en', 'ar', 'unknown']
     - Sentiment score BETWEEN -1 AND 1
     - word_count >= 0

3. **Validité (Validity)**
   - Definition: Data meets business rules
   - Threshold: ≥ 95%
   - Rules:
     - Article title: length >= 5 chars
     - Content: length >= 100 chars
     - Article: word_count >= 20 (Silver validation)
     - URL: valid HTTP(S) format

4. **Fraîcheur (Timeliness)**
   - Definition: Data recency
   - Threshold: ≤ 2h delay from source
   - Measurement:
     - Batch: Hourly (@hourly DAG)
     - Streaming: Near-real-time (< 5 min)
     - Silver: 1h delay max (2h from source)
     - Gold: 2h delay max (4h from source)
     - DWH: 4h delay max (from source)

### Quality Test Framework

**Automated Tests (Great Expectations):**

```python
# Bronze Layer
test_no_null_title()            # completude
test_no_null_content()          # completude
test_title_length_gt_5()        # validité
test_content_length_gt_100()    # validité
test_publication_date_not_future()  # validité

# Silver Layer
test_language_in_valid_values() # cohérence
test_sentiment_score_range()    # cohérence
test_no_keywords_empty()        # validité
test_word_count_ge_20()         # validité

# Gold Layer
test_source_id_not_null()       # cohérence
test_article_count_gt_0()       # validité
test_no_duplicate_source()      # cohérence

# DWH Layer
test_fact_article_id_unique()   # cohérence
test_foreign_key_references()   # validité
test_date_id_valid()            # cohérence
````

**Execution:**

- Run: `python quality/data_quality_checks.py`
- Frequency: After each transformation (after silver, after gold, after DWH load)
- Reporting: HTML report + logs
- Alert: Slack notification if pass rate < 95%

## Security & Access Control

### Authentication

- **MinIO:** User `minioadmin`, credentials in `.env`
- **PostgreSQL:** User `dwh_admin`, pwd in `.env`
- **Airflow:** Local authentication (airflow/airflow)

### Data Classification

| Layer  | Classification | Access                 |
| ------ | -------------- | ---------------------- |
| Bronze | Internal       | Data Team              |
| Silver | Internal       | Data + Analytics Teams |
| Gold   | Confidential   | Analytics + BI Teams   |
| DWH    | Confidential   | DWH + BI Teams + CFO   |

### Security Best Practices

- [x] Credentials in `.env` (not in code)
- [x] MinIO access key restricted to data operations only
- [x] PostgreSQL passwords hashed (PostgreSQL built-in)
- [x] Logs do not contain sensitive data
- [ ] SSL/TLS for production (not in MVP)
- [ ] Encryption at rest (not in MVP)
- [ ] Row-level security in PostgreSQL (not in MVP)

## Audit & Compliance

### Logging & Monitoring

**Tool:** Loguru (Python logging library)

```python
# Structured logs in /logs/ with rotation (7 days)
logger.info("Article scraped", extra={"article_id": "...", "source": "hespress"})
logger.error("Scraping failed", extra={"reason": "timeout", "retry_count": 3})
```

**Log Locations:**

- `/logs/scrapers_*.log` - Web scraping events
- `/logs/medallion_*.log` - Transformation events
- `/logs/warehouse_*.log` - DWH loading events
- Airflow: `/opt/airflow/logs/dag_id/task_id/`
- PostgreSQL: Configured in docker-compose

**Retention:** 7 days (rotated automatically)

### Data Lineage

- **Tool:** Manual tracking + Airflow DAG dependencies
- **Metadata:** article_id + timestamp in every table
- **Traceability:** Source → Bronze → Silver → Gold → DWH → Dashboard

### Audit Trail

Every record includes:

- `article_id`: Unique identifier
- `source`: Data source (hespress, bbc, etc.)
- `scraping_date`: When scraped (Bronze)
- `publication_date`: Original publish date
- Transformation timestamps implicit in file paths

## Data Retention & Lifecycle

| Layer  | Retention  | Reason                               | Action                      |
| ------ | ---------- | ------------------------------------ | --------------------------- |
| Bronze | 30 days    | Compliance, cost optimization        | Archive to S3 cold storage  |
| Silver | 90 days    | Audit, reprocessing capability       | Delete after 90d            |
| Gold   | 1 year     | Trend analysis, historical analytics | Archive after 1y            |
| DWH    | Indefinite | Business critical, trend tracking    | Never delete (backup daily) |

**Deletion Policy:**

- Automatic cleanup jobs (Cron jobs) run monthly
- Notify stakeholders 7 days before deletion
- Archival to S3 before deletion

## Disaster Recovery & Backup

### Backup Strategy

- **MinIO (Bronze/Silver/Gold):** Daily backup to external S3
- **PostgreSQL (DWH):** Continuous WAL archiving + daily full backup
- **Airflow DAGs:** Version controlled in Git
- **Documentation:** Stored in GitHub + local wiki

### RTO & RPO

| Component  | RTO (Recovery Time) | RPO (Recovery Point) |
| ---------- | ------------------- | -------------------- |
| MinIO      | 4 hours             | 1 day                |
| PostgreSQL | 1 hour              | 15 min               |
| Airflow    | 2 hours             | Latest DAG version   |

## Compliance & Standards

### Regulatory Alignment

- GDPR: Article anonymization (if applicable)
- Data Classification: Internal/Confidential
- Retention: 30-365 days per layer
- Audit: Complete logging + traceability

### Industry Best Practices

- [x] Architecture Médaillon (Databricks standard)
- [x] Star Schema (Kimball methodology)
- [x] Automated QA (Great Expectations)
- [x] Infrastructure as Code (Docker Compose)
- [x] Version control (Git)
- [x] Documentation (Markdown)

## Escalation & Support

### Support Matrix

| Issue               | Owner        | Contact      | SLA    |
| ------------------- | ------------ | ------------ | ------ |
| Data Quality Alert  | Data Steward | Team Slack   | 2h     |
| Airflow DAG Failure | DevOps       | Airflow logs | 1h     |
| Database Down       | DBA          | On-call      | 30 min |

### Change Management

- **Change Request:** Notify data team 48h before
- **Testing:** Dev environment before production
- **Rollback:** Keep previous 2 versions in backup
- **Documentation:** Update DATA_CATALOG.md immediately

## Key Contacts

- **Data Owner:** Pr. Lamia KARIM (encadrant)
- **Data Team:** Master IADATA students
- **Support:** Git Issues + Team Slack

```

**Livrables de phase:** 3 fichiers docs complets (12-15 pages total)

---

### ⏰ 12:00 - 13:30 | Pause Déjeuner (1.5h)

---

### ⏰ 13:30 - 17:00 | Relecture & Finitions Tous Docs (3.5h)

**Tâches:**
```

[ ] RAPPORT: Relecture finale orthographe
[ ] Vérifier tous liens internes (cross-references)
[ ] Valider format pages (header/footer)
[ ] Tester table des matières (clickable)
[ ] Export PDF final (validate)

[ ] PRÉSENTATION: Finaliser animations
[ ] Ajouter transitions par slide
[ ] Préparer speaker notes (1 phrase/slide)
[ ] Vérifier tous liens externes (si vidéo)
[ ] Test projecteur (16:9 format)

[ ] GOUVERNANCE: Polish 3 docs
[ ] Vérifier tables + formatting
[ ] Ajouter diagrammes Mermaid PNG
[ ] Tester liens markdown
[ ] Valider code samples

[ ] STRUCTURE FINALE:
[ ] Créer dossier LIVRABLE_FINAL/
[ ] Copier tous fichiers:
[ ] docker-compose.yml
[ ] requirements.txt
[ ] .env.example (secrets removed)
[ ] RAPPORT_FINAL.pdf
[ ] PRESENTATION_FINAL.pptx
[ ] README.md
[ ] /scrapers/
[ ] /dags/
[ ] /medallion/
[ ] /warehouse/
[ ] /dashboards/
[ ] /quality/
[ ] /docs/ (3 files)
[ ] Créer LIVRABLE_FINAL.zip

```

**Livrables de phase:** Tous documents finalisés + structure prête à soumettre

---

### ⏰ 17:00 - 20:00 | Validation Technique (3h)

**Objectif:** Vérifier que Docker Compose et code fonctionnent

```

[ ] Arrêter containers actuels
docker-compose down -v

[ ] Démarrer fresh
docker-compose up -d

[ ] Vérifier services (5-10 min)
docker-compose ps
└─ Tous services "Up"

[ ] Vérifier accès
[ ] MinIO console: http://localhost:9001
[ ] Airflow web: http://localhost:8080
[ ] Streamlit: http://localhost:8501
[ ] Metabase: http://localhost:3000

[ ] Lancer tests
python run_all_scrapers.py (max 15 articles)
└─ Vérifier: Bronze bucket créé

[ ] Vérifier data
[ ] Bronze: min 5 JSON files
[ ] PostgreSQL: Tables créées
docker exec news_dwh psql -U dwh_admin -d news_warehouse -c "\\dt"

[ ] Dashboard test
streamlit run dashboards/streamlit_app.py
└─ Vérifier: ≥ 3 visualisations chargées

[ ] Screenshot pour rapport
[ ] MinIO console (screenshot)
[ ] Airflow DAG graph (screenshot)
[ ] Dashboard Streamlit (3 screenshots)
[ ] PostgreSQL tables (screenshot)

```

**Livrables de phase:** Validation complète, screenshots pour rapport

---

### ⏰ 20:00 - 22:00 | Préparation Soutenance (2h)

**Tâches:**
```

[ ] Préparer salle de soutenance
[ ] Projector test (HDMI/USB-C)
[ ] Clicker/remote
[ ] Backup PDF sur clé USB
[ ] Internet backup (hotspot phone)

[ ] Préparer matériel
[ ] Imprimer 5 copies rapport
[ ] Préparer handouts (1-2 pages résumé)
[ ] Carte de visite team (optionnel)

[ ] Répétition orale
[ ] Présentation rapide (15 min)
[ ] Chronomètre
[ ] Anticiper questions (Q&A doc)

[ ] Derniers checks
[ ] Rapport: Relire résumé exécutif
[ ] PPT: Vérifier dernier slide (merci!)
[ ] Code: Démarrer Docker une dernière fois
[ ] Docs: Lire data catalog + lineage

```

**Livrables de jour:** Tout prêt pour soutenance 10 mai

**Temps total jour 3:** 14 heures ✅

---

## 📆 JOUR 4 - VENDREDI 10 MAI 2026 (avant 23:59 UTC)

### ⏰ Matin: Soumission Finale

```

[ ] Vérifier structure livrable:
LIVRABLE_FINAL/
├── README.md
├── RAPPORT_FINAL.pdf
├── PRESENTATION_FINAL.pptx
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── run_all_scrapers.py
├── scrapers/
├── dags/
├── medallion/
├── warehouse/
├── dashboards/
├── quality/
└── docs/
├── DATA_CATALOG.md
├── DATA_LINEAGE.md
└── GOVERNANCE_FRAMEWORK.md

[ ] Créer ZIP final:
Compress-Archive -Path "LIVRABLE_FINAL" -DestinationPath "LIVRABLE_FINAL.zip"

[ ] Vérifier taille (doit être < 200MB)
dir LIVRABLE_FINAL.zip

[ ] Envoyer par email avant 23:59 UTC
To: professeur@university.xx
Subject: [IADATA] Projet Big Data Architecture - Remise 10/05/2026
Body: "Veuillez trouver ci-joint notre livrable final..."

[ ] Garder preuve d'envoi (screenshot)

```

### ⏰ Après 23:59: Relaxation Méritée! 🎉

---

## ✅ FINAL CHECKLIST

```

RAPPORT FINAL.PDF ✅
├─ 25-30 pages
├─ Introduction + Archit + Implémentation + Résultats + Conclusion
├─ 15+ références bibliographiques  
└─ PDF A4, police 11pt, interligne 1.5

PRÉSENTATION FINAL.PPT ✅
├─ 30 slides
├─ 15-20 min de présentation
├─ Images + Diagrammes
└─ Speaker notes

CODE SOURCE ✅
├─ Tous fichiers Python
├─ docker-compose.yml
├─ requirements.txt
└─ .env.example

DOCUMENTATION ✅
├─ DATA_CATALOG.md
├─ DATA_LINEAGE.md
└─ GOVERNANCE_FRAMEWORK.md

STRUCTURE ✅
├─ LIVRABLE_FINAL/ folder
└─ LIVRABLE_FINAL.zip

VALIDATION ✅
├─ Docker Compose runs
├─ Services accessible
├─ Data flows end-to-end
└─ Dashboard working

SOUMISSION ✅
└─ Email envoyé avant deadline

```

---

## 📊 RÉSUMÉ TEMPS

| Activité | Jour 1 | Jour 2 | Jour 3 | Jour 4 | TOTAL |
|----------|--------|--------|--------|--------|-------|
| Rapport | 7h | 1h | 1h | - | 9h |
| Présentation | - | 3.5h | 0.5h | - | 4h |
| Gouvernance | - | - | 4h | - | 4h |
| Validation | - | - | 3h | 0.5h | 3.5h |
| Soumission | - | - | - | 0.5h | 0.5h |
| **TOTAL** | **12h** | **12h** | **14h** | **1h** | **39h** |

**Par personne (binôme):** 19.5h de travail focus

---

## 💡 CONSEIL FINAL

**À FAIRE ABSOLUMENT:**
1. Commencer demain matin (7 mai 8h)
2. Respecter timeline jour par jour
3. Ne pas modifier code les 2 derniers jours (risque bugs)
4. Garder copies de sauvegarde (cloud + USB)
5. Dormir la veille de la soutenance ✨

**À ÉVITER:**
- ❌ Perfectionner code = perte de temps
- ❌ Ajouter features nouvelles = trop tard
- ❌ Rédaction reportée au dernier jour
- ❌ Pas de preuve d'envoi = risque
- ❌ Oublier relecture orthographe

**BON COURAGE! 🚀**

---

*Plan préparé le 7 mai 2026 - À suivre strictement*
```
