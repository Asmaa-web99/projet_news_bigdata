# 📝 CHANGELOG - Détail des Modifications

**Date de refactorisation :** Mai 2026  
**Version du projet :** 1.0 → 1.1 (Production-Ready)

---

## 📊 RÉSUMÉ STATISTIQUE

| Métrique                      | Avant                        | Après                                                 |
| ----------------------------- | ---------------------------- | ----------------------------------------------------- |
| **DAGs Airflow**              | 3 séparés                    | 1 unifié                                              |
| **Points d'entrée**           | 3 commandes manuelles        | 1 commande (`docker-compose up --build`)              |
| **Fichiers de configuration** | 2 (docker-compose.yml, .env) | 2 (corrigés) + 1 Dockerfile                           |
| **Documentation**             | 1 README                     | 1 README + 4 docs additionnelles                      |
| **Scripts de lancement**      | 1 (start.ps1)                | 2 (start.ps1 + run_project.sh + verify_deployment.sh) |
| **Lignes de code nouveau**    | -                            | ~700 (DAG + scripts + Dockerfile)                     |

---

## 🔄 FICHIERS MODIFIÉS (Changements Détaillés)

### 1. `docker-compose.yml` - Infrastructure Docker

#### ❌ AVANT (Problèmes)

```yaml
kafka:
  environment:
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092 # ❌ ERREUR !
    # Services Docker ne peuvent pas atteindre localhost

airflow:
  image: apache/airflow:2.7.1 # ❌ Image statique
  # _PIP_ADDITIONAL_DEPENDENCIES: ...                       # ❌ Dépendances limitées
  # Pas de volumes pour quality/, data/                    # ❌ Incomplet
  # Pas de variables d'environnement pour services         # ❌ Communication bricolée
```

#### ✅ APRÈS (Corrigé)

```yaml
kafka:
  environment:
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092 # ✅ Correct - nom service Docker
    KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT
    KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT # ✅ Protocoles explicites

airflow:
  build:
    context: .
    dockerfile: Dockerfile # ✅ Image custom
  depends_on:
    kafka:
      condition: service_started # ✅ Attendre Kafka
    minio:
      condition: service_started # ✅ Attendre MinIO
    postgres_dwh:
      condition: service_started # ✅ Attendre DWH
  environment:
    - MINIO_ENDPOINT=minio:9000 # ✅ Nom service
    - KAFKA_BOOTSTRAP_SERVERS=kafka:9092 # ✅ Nom service
    - DWH_HOST=postgres_dwh # ✅ Nom service
    # + 5 autres variables pour cohérence                  # ✅ Complète
  volumes:
    - ./quality:/opt/airflow/quality # ✅ Volume quality
    - ./data:/opt/airflow/data # ✅ Volume data

networks:
  news_network:
    driver: bridge # ✅ Network explicite

metabase:
  environment:
    - MB_DB_TYPE=postgres # ✅ Connexion auto PostgreSQL
    - MB_DB_HOST=postgres_dwh # ✅ À travers network
```

**Lignes modifiées :** ~30  
**Impact :** Infrastructure robuste, communication inter-services fonctionnelle

---

### 2. `.env` - Variables d'Environnement

#### ❌ AVANT

```env
MINIO_ENDPOINT=localhost:9000           # ❌ localhost = erreur en Docker
DWH_HOST=localhost                       # ❌ localhost inaccessible de Airflow
DWH_PORT=5433                            # ❌ Port externe, pas le port interne
KAFKA_BROKER=localhost:9092              # ❌ localhost = pas accessible
```

#### ✅ APRÈS

```env
MINIO_ENDPOINT=minio:9000               # ✅ Nom service Docker
DWH_HOST=postgres_dwh                    # ✅ Nom service Docker
DWH_PORT=5432                            # ✅ Port interne (5433 est externe)
KAFKA_BOOTSTRAP_SERVERS=kafka:9092       # ✅ Nom service Docker

# + NOUVELLES VARIABLES
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=False
MB_DB_HOST=postgres_dwh                  # Metabase config auto
```

**Lignes modifiées :** 6 existantes + 7 nouvelles  
**Impact :** Variables d'environnement cohérentes avec Docker network

---

### 3. `requirements.txt` - Dépendances Python

#### ❌ AVANT

```
requests==2.31.0
beautifulsoup4==4.12.3
...
# Sans structure, sans Airflow providers
```

#### ✅ APRÈS

```
# ==== Core Data Processing ====
requests==2.31.0
beautifulsoup4==4.12.3
...

# ==== Apache Airflow ====
apache-airflow==2.7.1
apache-airflow-providers-postgres==5.7.1      # ✅ NOUVEAU
apache-airflow-providers-apache-kafka==1.2.0   # ✅ NOUVEAU
apache-airflow-providers-minio==3.3.0          # ✅ NOUVEAU
```

**Lignes ajoutées :** 12  
**Packages ajoutés :** 3 (Airflow providers)  
**Impact :** Dépendances complètes pour Airflow + communication services

---

### 4. `README.md` - Documentation Principale

#### Changes

- **Avant :** 300 lignes, focus sur Streamlit
- **Après :** 600+ lignes, focus sur architecture professionnelle

**Sections réécrites :**

- ✅ Titre + badges
- ✅ Objectif (aligné Big Data Enterprise)
- ✅ Démarrage rapide (3 options)
- ✅ Architecture globale (diagrammes ASCII)
- ✅ Structure du projet détaillée
- ✅ Pipeline d'exécution (flux complet)
- ✅ Architecture Médaillon (Bronze/Silver/Gold expliquée)
- ✅ Data Warehouse (Star Schema)
- ✅ Metabase dashboards
- ✅ Qualité données
- ✅ Gouvernance
- ✅ Troubleshooting

**Impact :** Document professionnel, prêt pour soutenance

---

## ✨ FICHIERS CRÉÉS (Complètement Nouveaux)

### 1. `Dockerfile` - Image Docker Custom

```dockerfile
FROM apache/airflow:2.7.1-python3.10

USER root
RUN apt-get update && apt-get install -y build-essential git curl

USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres==5.7.1 \
    apache-airflow-providers-apache-kafka==1.2.0 \
    apache-airflow-providers-minio==3.3.0

COPY --chown=airflow:root dags /opt/airflow/dags
COPY --chown=airflow:root scrapers /opt/airflow/scrapers
COPY --chown=airflow:root medallion /opt/airflow/medallion
COPY --chown=airflow:root warehouse /opt/airflow/warehouse
COPY --chown=airflow:root quality /opt/airflow/quality
COPY --chown=airflow:root data /opt/airflow/data
```

**Lignes:** 28  
**Purpose:** Builder image Airflow avec toutes dépendances + code projet  
**Impact :** Docker build cohérent, reproductible

---

### 2. `dags/news_pipeline_dag.py` - DAG Unifié PRINCIPAL

```python
# 450+ lignes
dag_id = 'news_bigdata_pipeline'
schedule_interval = '@hourly'

# Task 0: Setup environment
# Task 1: Scraping 5 sources (parallèles)
#   - scrape_hespress
#   - scrape_bbc
#   - scrape_akhbarona
#   - scrape_aljazeera
#   - scrape_franceinfo
# Task 2: bronze_to_silver_transformation
# Task 3: silver_to_gold_transformation
# Task 4: load_gold_to_dwh
# Task 5: data_quality_checks
# Task 6: prepare_metabase_dashboard
```

**Lignes:** 450+  
**Purpose:** Orchestration complète en 1 seul DAG  
**Impact :** Remplace 3 DAGs séparés par 1 orchestration cohérente

---

### 3. `run_project.sh` - Script Lancement Unifié

```bash
#!/bin/bash
# - Vérification Docker
# - Arrêt containers existants
# - docker-compose up --build
# - Affichage URLs services
# - Troubleshooting guide
# - Options CLI : --logs, --down, --clean
```

**Lignes:** 180+  
**Purpose:** Point d'entrée unique professionnel  
**Impact :** Professeur lance 1 script au lieu de 3 commandes

---

### 4. `governance/data_catalog.md` - Gouvernance Données

```markdown
# 800+ lignes avec:

- Dictionnaire de données (20+ champs)
- Description couches Médaillon
- Schémas Parquet
- Star Schema PostgreSQL (DDL complet)
- Vues analytiques
- Tests qualité (4 dimensions)
- Lineage des données
- Conformité RGPD
- SLAs opérationnels
- Changelog et roadmap
```

**Lignes:** 800+  
**Purpose:** Documentation gouvernance exhaustive  
**Impact :** Montre que la gouvernance data est prise au sérieux

---

### 5. `DEPLOYMENT_SUMMARY.md` - Résumé Refactorisation

```markdown
# 400+ lignes avec:

- Modifications détaillées fichier par fichier
- Checklist validation
- Commandes utiles
- Guide présentation professeur
- Points clés à souligner
```

**Lignes:** 400+  
**Purpose:** Résumé complet pour vérification  
**Impact :** Traçabilité totale des modifications

---

### 6. `QUICK_REFERENCE.md` - Lancerment Rapide

```markdown
# Référence rapide 30 secondes

- 3 étapes pour lancer
- URLs services
- Checklist rapide
- Commandes d'arrêt
```

**Lignes:** 50  
**Purpose:** Guide ultra-rapide  
**Impact :** Professeur sait immédiatement comment lancer

---

### 7. `verify_deployment.sh` - Validation Script

```bash
#!/bin/bash
# - Vérifie tous les fichiers
# - Valide contenu critique
# - Affiche résumé final
# - Exit code OK/FAIL
```

**Lignes:** 180+  
**Purpose:** Validation automatisée de la refactorisation  
**Impact :** Assurer que rien n'est cassé

---

### 8. `REFACTORING_COMPLETE.md` - Résumé Exécutif

```markdown
# Résumé visuellement agréable avec:

- Diagrammes "avant/après"
- Points clés surlignés
- Checklist validation
- Guide démonstration 10 min
```

**Lignes:** 400+  
**Purpose:** Vue d'ensemble pour le professeur  
**Impact :** "Wow" factor professionnel

---

## 🔐 FICHIERS PRÉSERVÉS (AUCUN SUPPRIMÉ !)

### Code Existant Conservé

| Composant                   | Fichiers                                       | Status    |
| --------------------------- | ---------------------------------------------- | --------- |
| **Scrapers**                | `scrapers/base_scraper.py` + 5 implémentations | ✅ Intact |
| **Medallion Bronze→Silver** | `medallion/bronze_to_silver.py`                | ✅ Intact |
| **Medallion Silver→Gold**   | `medallion/silver_to_gold.py`                  | ✅ Intact |
| **DWH Loader**              | `warehouse/load_to_dwh.py`                     | ✅ Intact |
| **Schéma DWH**              | `warehouse/schema.sql`                         | ✅ Intact |
| **Qualité Données**         | `quality/data_quality_checks.py`               | ✅ Intact |
| **Streaming Kafka**         | `streaming/*`                                  | ✅ Intact |
| **Dashboard Streamlit**     | `dashboards/streamlit_app.py`                  | ✅ Intact |
| **Variables d'env**         | `.env.example`                                 | ✅ Intact |

### Anciens DAGs (Archivés - Peuvent être Supprimés)

- `dags/dag_batch_scraping.py` → Remplacé par `news_pipeline_dag.py`
- `dags/dag_medallion_pipeline.py` → Remplacé par `news_pipeline_dag.py`
- `dags/dag_dwh_loading.py` → Remplacé par `news_pipeline_dag.py`

**Note :** Ces fichiers peuvent être supprimés sans danger (remplacement complet)

---

## 📈 IMPACT RÉSUMÉ

### Avant la Refactorisation

- ❌ 3 DAGs à orchestrer manuellement
- ❌ Kafka utilise localhost (erreur Docker)
- ❌ Variables d'env incohérentes
- ❌ Documentation fragmentée
- ❌ Pas de point d'entrée unique
- ⚠️ Présentation académique difficile

### Après la Refactorisation

- ✅ 1 DAG unifié `news_bigdata_pipeline`
- ✅ Kafka utilise `kafka:9092` (communication inter-conteneur)
- ✅ Variables d'env cohérentes avec Docker network
- ✅ Documentation complète (README + governance + guides)
- ✅ Point d'entrée unique `docker-compose up --build`
- ✅ Présentation académique professionnelle

---

## 🎯 VALIDATION

Tous les changements ont été :

- ✅ Testés pour validité syntaxe
- ✅ Alignés avec architecture Medallion
- ✅ Compatibles avec architecture existante
- ✅ Documentés dans ce fichier
- ✅ Résumés dans DEPLOYMENT_SUMMARY.md
- ✅ Validables via verify_deployment.sh

---

## 📞 SUPPORT

En cas de question :

1. Consulter `DEPLOYMENT_SUMMARY.md`
2. Vérifier via `./verify_deployment.sh`
3. Lancer avec `./run_project.sh`
4. Consulter logs : `docker-compose logs`

---

**Refactorisation complétée avec succès ! ✨**
