#!/bin/bash

##############################################################################
#
# 🚀 Script de Lancement Unifié - News Big Data Platform
#
# Usage:
#   ./run_project.sh          # Lancer normalement (mode production)
#   ./run_project.sh --logs   # Afficher les logs en continu
#   ./run_project.sh --down   # Arrêter tous les services
#   ./run_project.sh --clean  # Nettoyer tous les volumes
#
##############################################################################

set -e  # Arrêter à la première erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_NAME="news-bigdata-platform"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

##############################################################################
# FONCTIONS
##############################################################################

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé ou non accessible"
        exit 1
    fi
    log_success "Docker trouvé : $(docker --version)"
}

check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    log_success "Docker Compose trouvé : $(docker-compose --version)"
}

cleanup_containers() {
    log_info "Arrêt des conteneurs existants..."
    docker-compose -f "$PROJECT_DIR/docker-compose.yml" down 2>/dev/null || true
    sleep 2
    log_success "Conteneurs arrêtés"
}

cleanup_volumes() {
    log_warning "Suppression de tous les volumes persistants..."
    docker volume rm news_minio news_dwh 2>/dev/null || true
    log_success "Volumes supprimés"
}

build_and_start() {
    log_info "Construction et démarrage des conteneurs..."
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose.yml up --build -d
    
    # Attendre que les services soient prêts
    log_info "Attente du démarrage des services (30 secondes)..."
    sleep 30
    
    log_success "Conteneurs démarrés"
}

show_services_status() {
    log_info "📊 État des services :"
    echo ""
    docker-compose -f "$PROJECT_DIR/docker-compose.yml" ps
    echo ""
}

show_access_urls() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║          🎯 ACCÈS AUX INTERFACES WEB                       ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║                                                            ║"
    echo -e "║  ${BLUE}🔵 Airflow (Orchestration)${NC}"
    echo "║     URL : http://localhost:8080"
    echo "║     User : airflow / Password : airflow"
    echo "║     DAG : news_bigdata_pipeline"
    echo "║                                                            ║"
    echo -e "║  ${BLUE}🟠 MinIO (Data Lake)${NC}"
    echo "║     URL : http://localhost:9001"
    echo "║     User : minioadmin / Password : minioadmin"
    echo "║     Buckets : bronze, silver, gold"
    echo "║                                                            ║"
    echo -e "║  ${BLUE}🟢 Metabase (Dashboard BI)${NC}"
    echo "║     URL : http://localhost:3000"
    echo "║     Setup initial : configure PostgreSQL comme source"
    echo "║                                                            ║"
    echo -e "║  ${BLUE}🟡 PostgreSQL (Data Warehouse)${NC}"
    echo "║     Host : localhost:5433"
    echo "║     DB : news_warehouse"
    echo "║     User : dwh_admin / Password : dwh_password"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

show_troubleshooting() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║          🔧 COMMANDES UTILES & TROUBLESHOOTING             ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║                                                            ║"
    echo "║  📜 Logs Airflow :"
    echo "║     docker-compose logs airflow"
    echo "║                                                            ║"
    echo "║  📜 Logs Kafka :"
    echo "║     docker-compose logs kafka"
    echo "║                                                            ║"
    echo "║  📜 Logs MinIO :"
    echo "║     docker-compose logs minio"
    echo "║                                                            ║"
    echo "║  Connecter à PostgreSQL :"
    echo "║     psql -h localhost -U dwh_admin -d news_warehouse"
    echo "║                                                            ║"
    echo "║  Arrêter complètement :"
    echo "║     docker-compose down"
    echo "║                                                            ║"
    echo "║  Nettoyer (données incluses) :"
    echo "║     docker-compose down -v"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

view_logs() {
    log_info "Affichage des logs en temps réel (Ctrl+C pour arrêter)..."
    echo ""
    docker-compose -f "$PROJECT_DIR/docker-compose.yml" logs -f
}

##############################################################################
# MAIN
##############################################################################

main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║     📰 NEWS BIG DATA PLATFORM - Launcher Unifié            ║"
    echo "║                                                            ║"
    echo "║  Transforme vos données de news en insights exploitables  ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    # Traiter les arguments
    case "${1:-}" in
        --logs)
            log_info "Mode logs - affichage en continu..."
            view_logs
            ;;
        --down)
            log_warning "Arrêt de tous les services..."
            cleanup_containers
            log_success "Services arrêtés"
            ;;
        --clean)
            log_warning "Nettoyage complet (y compris données)..."
            cleanup_containers
            cleanup_volumes
            log_success "Nettoyage complet effectué"
            ;;
        *)
            # Mode normal
            check_docker
            check_docker_compose
            
            log_info "🔄 Arrêt des conteneurs existants..."
            cleanup_containers
            
            log_info "🏗️  Construction et démarrage..."
            build_and_start
            
            log_success "✨ Plateforme démarrée avec succès !"
            
            show_services_status
            show_access_urls
            show_troubleshooting
            
            echo ""
            log_info "💡 Conseil : Le DAG 'news_bigdata_pipeline' s'exécutera automatiquement chaque heure"
            log_info "            ou vous pouvez le déclencher manuellement depuis Airflow UI"
            echo ""
            ;;
    esac
}

# Lancer
main "$@"
