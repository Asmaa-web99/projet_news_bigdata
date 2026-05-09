# 🚀 DÉMARRAGE RAPIDE (2 MINUTES)

## ⚠️ Prérequis

- **Docker Desktop** installé et lancé
- **Git** installé
- ~5 GB d'espace disque libre
- Ports disponibles : 8080, 8501, 5433, 9000, 9092

---

## 📋 Étapes

### **1️⃣ Cloner le projet**

```bash
git clone https://github.com/Asmaa-web99/projet_news_bigdata.git
cd projet_news_bigdata
```

### **2️⃣ Démarrer tous les services (1 commande)**

```bash
docker-compose up -d
```

Cela va démarrer :

- ✅ MinIO (Data Lake)
- ✅ Kafka (Streaming)
- ✅ PostgreSQL (Data Warehouse)
- ✅ Airflow (Orchestration)
- ✅ Metabase (BI)
- ✅ Streamlit (Dashboard)

### **3️⃣ Attendre 2-3 minutes** ⏳

Services à démarrer en arrière-plan...

### **4️⃣ Lancer le Pipeline**

#### **Option A : Dashboard Streamlit (Recommandé pour voir les résultats)**

```bash
# Ouvrir dans le navigateur
http://localhost:8501
```

#### **Option B : Airflow UI (Pour voir l'orchestration)**

```bash
# Aller à
http://localhost:8080

# Login:
# Username: airflow
# Password: airflow

# Activer et déclencher le DAG "dag_batch_scraping"
```

#### **Option C : MinIO (Pour voir le Data Lake)**

```bash
# Aller à
http://localhost:9001

# Login:
# Username: minioadmin
# Password: minioadmin
```

---

## 📊 Résultats attendus

| Service                 | URL                   | Fonction                                         |
| ----------------------- | --------------------- | ------------------------------------------------ |
| **Streamlit Dashboard** | http://localhost:8501 | 📊 Visualisation articles, sentiments, tendances |
| **Airflow**             | http://localhost:8080 | 🔄 Orchestration des pipelines                   |
| **MinIO Console**       | http://localhost:9001 | 💾 Data Lake (Bronze/Silver/Gold)                |
| **Metabase**            | http://localhost:3000 | 📈 Business Intelligence avancée                 |
| **PostgreSQL DWH**      | localhost:5433        | 🗄️ Data Warehouse relationnel                    |

---

## ✅ Vérifier que tout fonctionne

```bash
# Vérifier l'état des conteneurs
docker-compose ps

# Doit afficher tous les services en "Up"
```

Output attendu:

```
NAME              STATUS
news_minio        Up 2 minutes
news_kafka        Up 2 minutes
news_zookeeper    Up 2 minutes
news_dwh          Up 2 minutes
news_airflow      Up 2 minutes
news_streamlit    Up 2 minutes
news_metabase     Up 2 minutes
```

---

## 🛑 Arrêter le projet

```bash
docker-compose down
```

Pour tout supprimer (volumes, données) :

```bash
docker-compose down -v
```

---

## ⚠️ Problèmes courants

### "Port already in use"

```bash
# Changer le port dans docker-compose.yml
# Exemple : "8080:8080" → "8081:8080"
```

### "Docker not running"

→ Ouvrir Docker Desktop

### "Services ne démarrent pas"

```bash
# Voir les logs
docker-compose logs

# Redémarrer
docker-compose restart
```

---

## 📁 Structure du Projet

```
projet_news_bigdata/
├── scrapers/           ← Web scrapers (5 sources)
├── medallion/          ← Bronze/Silver/Gold pipelines
├── dags/               ← Airflow DAGs (orchestration)
├── dashboards/         ← Streamlit app
├── warehouse/          ← PostgreSQL schema
├── quality/            ← Tests de qualité
└── docker-compose.yml  ← Configuration
```

---

## 🎓 Pour le rapport

Le code et la configuration sont dans ce dossier :

- **Code source :** `scrapers/`, `medallion/`, `dags/`, `dashboards/`, `warehouse/`
- **Configuration :** `docker-compose.yml`, `.env.example`
- **Documentation :** `README.md`
- **Rapport académique :** `rapport/main.pdf`

---

**Questions?** Voir le README.md complet pour plus de détails. 📖
