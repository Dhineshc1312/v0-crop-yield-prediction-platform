#!/bin/bash

# Deployment script for SIH AI Harvesters Platform
# Handles production deployment with zero-downtime updates

set -e

# Configuration
PROJECT_NAME="sih-ai-harvesters"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        error ".env file not found. Please create it from .env.example"
        exit 1
    fi
    log "✅ Environment file found"
}

# Create necessary directories
setup_directories() {
    mkdir -p "$BACKUP_DIR" logs nginx/ssl
    log "✅ Directories created"
}

# Generate SSL certificates (self-signed for development)
generate_ssl() {
    if [ ! -f nginx/ssl/cert.pem ]; then
        log "Generating self-signed SSL certificates..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=IN/ST=Odisha/L=Bhubaneswar/O=SIH AI Harvesters/CN=localhost"
        log "✅ SSL certificates generated"
    else
        log "✅ SSL certificates already exist"
    fi
}

# Backup database
backup_database() {
    if [ "$1" = "production" ]; then
        log "Creating database backup..."
        python scripts/backup_database.py create
        log "✅ Database backup created"
    fi
}

# Build and deploy
deploy() {
    local environment=${1:-development}
    
    log "🚀 Starting deployment for $environment environment..."
    
    # Load environment variables
    source .env
    
    # Choose compose file based on environment
    if [ "$environment" = "production" ]; then
        COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
    else
        COMPOSE_FILES="-f docker-compose.yml -f docker-compose.override.yml"
    fi
    
    # Pull latest images
    log "Pulling latest images..."
    docker-compose $COMPOSE_FILES pull
    
    # Build services
    log "Building services..."
    docker-compose $COMPOSE_FILES build --no-cache
    
    # Stop existing services
    log "Stopping existing services..."
    docker-compose $COMPOSE_FILES down
    
    # Start services
    log "Starting services..."
    docker-compose $COMPOSE_FILES up -d
    
    # Wait for services to be healthy
    log "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_health
    
    log "🎉 Deployment completed successfully!"
}

# Health check
check_health() {
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log "✅ API service is healthy"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            error "API service failed to start"
            docker-compose logs api
            exit 1
        fi
        
        log "Waiting for API service... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    # Check frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log "✅ Frontend service is healthy"
    else
        warning "Frontend service may not be ready"
    fi
}

# Rollback function
rollback() {
    log "🔄 Rolling back to previous version..."
    
    # Stop current services
    docker-compose down
    
    # Restore database backup if exists
    local latest_backup=$(ls -t "$BACKUP_DIR"/sih_ai_harvesters_backup_*.sql* 2>/dev/null | head -n1)
    if [ -n "$latest_backup" ]; then
        log "Restoring database from backup: $latest_backup"
        python scripts/backup_database.py restore "$latest_backup"
    fi
    
    # Start services with previous images
    docker-compose up -d
    
    log "✅ Rollback completed"
}

# Cleanup old images and containers
cleanup() {
    log "🧹 Cleaning up old Docker resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused volumes (be careful with this)
    # docker volume prune -f
    
    log "✅ Cleanup completed"
}

# Show logs
show_logs() {
    local service=${1:-}
    
    if [ -n "$service" ]; then
        docker-compose logs -f "$service"
    else
        docker-compose logs -f
    fi
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        check_env
        setup_directories
        generate_ssl
        backup_database "${2:-development}"
        deploy "${2:-development}"
        ;;
    "rollback")
        rollback
        ;;
    "cleanup")
        cleanup
        ;;
    "logs")
        show_logs "$2"
        ;;
    "health")
        check_health
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|cleanup|logs|health} [environment|service]"
        echo ""
        echo "Commands:"
        echo "  deploy [production|development]  - Deploy the application"
        echo "  rollback                         - Rollback to previous version"
        echo "  cleanup                          - Clean up old Docker resources"
        echo "  logs [service]                   - Show logs for all services or specific service"
        echo "  health                           - Check service health"
        echo ""
        echo "Examples:"
        echo "  $0 deploy production"
        echo "  $0 logs api"
        echo "  $0 rollback"
        exit 1
        ;;
esac
