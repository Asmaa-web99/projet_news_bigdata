# ⚡ QUICK REFERENCE - Lancement Rapide

## 🚀 EN 30 SECONDES

```bash
# 1. Aller au répertoire projet
cd news-bigdata-project

# 2. Lancer le tout
docker-compose up --build

# 3. Attendre 30 secondes, puis ouvrir :
```

## 📍 ACCÈS AUX SERVICES

| Service        | URL                   | User/Pass                |
| -------------- | --------------------- | ------------------------ |
| **Airflow**    | http://localhost:8080 | airflow / airflow        |
| **MinIO**      | http://localhost:9001 | minioadmin / minioadmin  |
| **Metabase**   | http://localhost:3000 | À configurer             |
| **PostgreSQL** | localhost:5433        | dwh_admin / dwh_password |

## 🎯 DAG EXÉCUTÉ AUTOMATIQUEMENT

DAG: **`news_bigdata_pipeline`**

Flux:

```
Scraping (5 sources)
  → Bronze (MinIO)
  → Silver (NLP)
  → Gold (Agrégation)
  → DWH (PostgreSQL)
  → Qualité + Metabase
```

Schedule: **@hourly** (toutes les heures)

## ✅ CHECKLIST RAPIDE

- [ ] Tous les services "Up" : `docker-compose ps`
- [ ] Airflow accessible : http://localhost:8080
- [ ] DAG `news_bigdata_pipeline` visible et exécuté (vert)
- [ ] MinIO contient articles en `/bronze/`, `/silver/`, `/gold/`
- [ ] PostgreSQL contient articles : `SELECT COUNT(*) FROM fact_article;`

## 🛑 ARRÊT

```bash
# Arrêter services (données conservées)
docker-compose down

# Arrêter + supprimer données
docker-compose down -v
```

## 📚 DOCUMENTATION COMPLÈTE

- **README.md** - Guide détaillé
- **governance/data_catalog.md** - Dictionnaire données & lineage
- **DEPLOYMENT_SUMMARY.md** - Résumé refactorisation
- **dags/news_pipeline_dag.py** - Code DAG commenté

---

**Prêt ? Lancez : `docker-compose up --build` 🚀**
