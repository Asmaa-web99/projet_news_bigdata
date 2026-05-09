#!/bin/bash

##############################################################################
#
# ✅ VALIDATION CHECKLIST - News Big Data Platform
#
# Ce script vérifie que tous les fichiers ont été créés/modifiés correctement
# et que le projet est prêt pour lancement.
#
# Usage: ./verify_deployment.sh
#
##############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CHECKS_PASSED=0
CHECKS_FAILED=0

# Fonction de vérification
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $description"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}❌${NC} $description (MANQUANT: $file)"
        ((CHECKS_FAILED++))
    fi
}

check_dir() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅${NC} $description"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}❌${NC} $description (MANQUANT: $dir)"
        ((CHECKS_FAILED++))
    fi
}

check_content() {
    local file=$1
    local pattern=$2
    local description=$3
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $description"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}❌${NC} $description (CONTENU: $file)"
        ((CHECKS_FAILED++))
    fi
}

# =====================================================================
# DÉBUT DES VÉRIFICATIONS
# =====================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║    🔍 VALIDATION DÉPLOIEMENT NEWS BIG DATA PLATFORM       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ------- FICHIERS CRITIQUES CRÉÉS/MODIFIÉS -------

echo -e "${BLUE}📋 Fichiers Infrastructure${NC}"
check_file "docker-compose.yml" "docker-compose.yml (corrigé)"
check_file "Dockerfile" "Dockerfile (nouveau)"
check_file ".env" ".env (variables mises à jour)"
check_content "docker-compose.yml" "kafka:9092" "Kafka intra-Docker (pas localhost)"
check_content ".env" "minio:9000" ".env : MINIO_ENDPOINT = minio:9000"
check_content ".env" "postgres_dwh" ".env : DWH_HOST = postgres_dwh"

echo ""
echo -e "${BLUE}🐍 Dépendances Python${NC}"
check_file "requirements.txt" "requirements.txt (amélioré)"
check_content "requirements.txt" "apache-airflow-providers-postgres" "Airflow provider PostgreSQL"
check_content "requirements.txt" "apache-airflow-providers-apache-kafka" "Airflow provider Kafka"
check_content "requirements.txt" "apache-airflow-providers-minio" "Airflow provider MinIO"

echo ""
echo -e "${BLUE}🔄 Orchestration Airflow${NC}"
check_file "dags/news_pipeline_dag.py" "DAG unifié news_pipeline_dag.py (NOUVEAU)"
check_content "dags/news_pipeline_dag.py" "news_bigdata_pipeline" "DAG ID = news_bigdata_pipeline"
check_content "dags/news_pipeline_dag.py" "@hourly" "Schedule = @hourly"
check_content "dags/news_pipeline_dag.py" "scrape_hespress" "Task scrape_hespress"
check_content "dags/news_pipeline_dag.py" "bronze_to_silver_transformation" "Task bronze_to_silver"
check_content "dags/news_pipeline_dag.py" "silver_to_gold_transformation" "Task silver_to_gold"
check_content "dags/news_pipeline_dag.py" "load_gold_to_dwh" "Task load_gold_to_dwh"

echo ""
echo -e "${BLUE}🚀 Scripts de Lancement${NC}"
check_file "run_project.sh" "run_project.sh (nouveau)"
check_content "run_project.sh" "docker-compose up --build" "Script contient docker-compose up"
check_content "run_project.sh" "http://localhost:8080" "Script affiche URLs Airflow"
check_content "run_project.sh" "http://localhost:9001" "Script affiche URLs MinIO"

echo ""
echo -e "${BLUE}📚 Documentation${NC}"
check_file "README.md" "README.md (réécrit - professionnel)"
check_file "governance/data_catalog.md" "governance/data_catalog.md (nouveau)"
check_content "README.md" "news_bigdata_pipeline" "README mentionne DAG unifié"
check_content "README.md" "docker-compose up --build" "README contient commande lancement"
check_content "governance/data_catalog.md" "Bronze Layer" "Catalogue décrit couche Bronze"
check_content "governance/data_catalog.md" "Silver Layer" "Catalogue décrit couche Silver"
check_content "governance/data_catalog.md" "Gold Layer" "Catalogue décrit couche Gold"
check_content "governance/data_catalog.md" "Star Schema" "Catalogue décrit DWH Schema"

echo ""
echo -e "${BLUE}📁 Répertoires & Structures${NC}"
check_dir "dags" "Répertoire dags/"
check_dir "scrapers" "Répertoire scrapers/"
check_dir "medallion" "Répertoire medallion/"
check_dir "warehouse" "Répertoire warehouse/"
check_dir "quality" "Répertoire quality/"
check_dir "governance" "Répertoire governance/ (nouveau)"

echo ""
echo -e "${BLUE}🔐 Fichiers Préservés${NC}"
check_file "scrapers/base_scraper.py" "Base scraper préservé"
check_file "scrapers/hespress_scraper.py" "Hespress scraper préservé"
check_file "scrapers/bbc_scraper.py" "BBC scraper préservé"
check_file "medallion/bronze_to_silver.py" "Bronze→Silver pipeline préservé"
check_file "medallion/silver_to_gold.py" "Silver→Gold pipeline préservé"
check_file "warehouse/load_to_dwh.py" "DWH loader préservé"
check_file "quality/data_quality_checks.py" "Quality framework préservé"

echo ""
echo -e "${BLUE}📊 Fichiers Additionnels${NC}"
check_file "DEPLOYMENT_SUMMARY.md" "DEPLOYMENT_SUMMARY.md (résumé refactorisation)"

# ------- VÉRIFICATIONS DE CONTENU CRITIQUE -------

echo ""
echo -e "${BLUE}🔍 Validations de Contenu${NC}"

# Vérifier que les 3 anciens DAGs existent toujours (pour backup)
if [ -f "dags/dag_batch_scraping.py" ]; then
    echo -e "${YELLOW}⚠️ ${NC}  dag_batch_scraping.py archivé (peut être supprimé)"
    ((CHECKS_PASSED++))
fi

if [ -f "dags/dag_medallion_pipeline.py" ]; then
    echo -e "${YELLOW}⚠️ ${NC}  dag_medallion_pipeline.py archivé (peut être supprimé)"
    ((CHECKS_PASSED++))
fi

if [ -f "dags/dag_dwh_loading.py" ]; then
    echo -e "${YELLOW}⚠️ ${NC}  dag_dwh_loading.py archivé (peut être supprimé)"
    ((CHECKS_PASSED++))
fi

# Vérifier docker-compose corrections
check_content "docker-compose.yml" "build:" "Airflow utilise Dockerfile custom"
check_content "docker-compose.yml" "KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092" "Kafka correctement configuré"
check_content "docker-compose.yml" "DWH_HOST=postgres_dwh" "DWH_HOST utilise nom service"

# ------- RÉSUMÉ FINAL -------

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   📊 RÉSUMÉ VALIDATION                      ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo -e "║  ${GREEN}✅ Vérifications réussies${NC} : ${GREEN}$CHECKS_PASSED${NC}"
echo -e "║  ${RED}❌ Vérifications échouées${NC}  : ${RED}$CHECKS_FAILED${NC}"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 SUCCÈS ! Tous les fichiers sont en place.${NC}"
    echo ""
    echo "Prêt pour lancement :"
    echo -e "  ${BLUE}cd news-bigdata-project${NC}"
    echo -e "  ${BLUE}./run_project.sh${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  Des fichiers manquent ou sont incorrects.${NC}"
    echo "Veuillez résoudre les problèmes signalés ci-dessus."
    echo ""
    exit 1
fi
