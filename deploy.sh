#!/bin/bash
# ==============================================================================
# deploy.sh - Full Deployment Automation Script
# Language Learning Agent - Cloud Infrastructure
# ==============================================================================
# Usage:
#   ./deploy.sh docker     → Build & run with Docker Compose
#   ./deploy.sh minikube   → Deploy to local Minikube cluster
#   ./deploy.sh stop       → Stop all services
#   ./deploy.sh status     → Show running services status
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  🎓 Language Learning Agent - Deployment Automation        ║"
    echo "║  Powered by: Asser Almasry | AI Engineer                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ─── Docker Compose Deployment ───────────────────────────────────────────────
deploy_docker() {
    echo -e "${BLUE}[1/4]${NC} Building Docker images..."
    docker compose build --no-cache

    echo -e "${BLUE}[2/4]${NC} Starting services with resource limits..."
    docker compose up -d

    echo -e "${BLUE}[3/4]${NC} Waiting for health checks..."
    sleep 15

    echo -e "${BLUE}[4/4]${NC} Verifying deployment..."
    docker compose ps

    echo ""
    echo -e "${GREEN}✅ Deployment Complete!${NC}"
    echo -e "   🌐 Application:      ${YELLOW}http://localhost${NC}"
    echo -e "   📊 Grafana Dashboard: ${YELLOW}http://localhost:3001${NC}"
    echo -e "      Login: admin / avs5g962HaY2IpIJZgQvyg"
    echo ""
    echo -e "${BLUE}📈 Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
}

# ─── Minikube Deployment ─────────────────────────────────────────────────────
deploy_minikube() {
    echo -e "${BLUE}[1/7]${NC} Starting Minikube cluster..."
    minikube start --cpus 4 --memory 10240 --driver=docker

    echo -e "${BLUE}[2/7]${NC} Enabling NGINX Ingress addon..."
    minikube addons enable ingress
    minikube addons enable metrics-server

    echo -e "${BLUE}[3/7]${NC} Switching to Minikube Docker daemon..."
    eval $(minikube docker-env)

    echo -e "${BLUE}[4/7]${NC} Building images inside Minikube..."
    docker build -f Dockerfile.backend -t lang-agent/api-backend:latest .
    docker build -f Dockerfile.frontend -t lang-agent/frontend-ui:latest .

    echo -e "${BLUE}[5/7]${NC} Applying Kubernetes manifests..."
    kubectl apply -f k8s/00-namespace.yaml
    kubectl apply -f k8s/01-secrets-configmap.yaml
    kubectl apply -f k8s/02-persistent-volumes.yaml
    kubectl apply -f k8s/03-backend-deployment.yaml
    kubectl apply -f k8s/04-frontend-deployment.yaml
    kubectl apply -f k8s/05-chromadb-statefulset.yaml
    kubectl apply -f k8s/06-ingress.yaml
    kubectl apply -f k8s/07-monitoring.yaml

    echo -e "${BLUE}[6/7]${NC} Waiting for pods to become ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=lang-agent \
        -n lang-agent --timeout=180s 2>/dev/null || true
    sleep 10

    echo -e "${BLUE}[7/7]${NC} Deployment status:"
    kubectl get all -n lang-agent

    MINIKUBE_IP=$(minikube ip)
    echo ""
    echo -e "${GREEN}✅ Minikube Deployment Complete!${NC}"
    echo -e "   🌐 Application:      ${YELLOW}http://${MINIKUBE_IP}${NC}"
    echo -e "   📊 Grafana Dashboard: ${YELLOW}http://${MINIKUBE_IP}:31000${NC}"
    echo -e "      Login: admin / avs5g962HaY2IpIJZgQvyg"
    echo ""
    echo -e "${BLUE}To access via tunnel:${NC} minikube tunnel"
    echo -e "${BLUE}To view pod logs:${NC}    kubectl logs -f deploy/api-backend -n lang-agent"
    echo -e "${BLUE}To check resources:${NC} kubectl top pods -n lang-agent"
}

# ─── Huawei Cloud (CCE) Deployment ───────────────────────────────────────────
deploy_huawei() {
    # Replace these with your actual Huawei Cloud details
    SWR_ENDPOINT="swr.ap-southeast-1.myhuaweicloud.com" # Example: Singapore
    ORGANIZATION="lang-agent-project"
    
    echo -e "${YELLOW}⚠️  Note: Ensure you have run 'docker login' for SWR and set your kubectl context to CCE.${NC}"
    
    echo -e "${BLUE}[1/5]${NC} Building production images..."
    docker build -f Dockerfile.backend -t ${SWR_ENDPOINT}/${ORGANIZATION}/api-backend:v1 .
    docker build -f Dockerfile.frontend -t ${SWR_ENDPOINT}/${ORGANIZATION}/frontend-ui:v1 .

    echo -e "${BLUE}[2/5]${NC} Pushing images to Huawei SWR..."
    docker push ${SWR_ENDPOINT}/${ORGANIZATION}/api-backend:v1
    docker push ${SWR_ENDPOINT}/${ORGANIZATION}/frontend-ui:v1

    echo -e "${BLUE}[3/5]${NC} Preparing Kubernetes manifests..."
    # Update image paths in manifests (temporary sed)
    mkdir -p k8s/cloud-build
    cp k8s/*.yaml k8s/cloud-build/
    sed -i "s|image: lang-agent/|image: ${SWR_ENDPOINT}/${ORGANIZATION}/|g" k8s/cloud-build/*.yaml

    echo -e "${BLUE}[4/5]${NC} Deploying to Huawei CCE..."
    kubectl apply -f k8s/cloud-build/00-namespace.yaml
    kubectl apply -f k8s/cloud-build/01-secrets-configmap.yaml
    kubectl apply -f k8s/cloud-build/02-persistent-volumes.yaml
    kubectl apply -f k8s/cloud-build/03-backend-deployment.yaml
    kubectl apply -f k8s/cloud-build/04-frontend-deployment.yaml
    kubectl apply -f k8s/cloud-build/05-chromadb-statefulset.yaml
    kubectl apply -f k8s/cloud-build/06-ingress.yaml

    echo -e "${BLUE}[5/5]${NC} Verifying Cloud Status..."
    kubectl get pods -n lang-agent
    
    echo ""
    echo -e "${GREEN}🚀 Huawei Cloud Deployment Initiated!${NC}"
    echo -e "   Check your Load Balancer IP in the Huawei Console (Network -> ELB)."
}

# ─── Stop All Services ───────────────────────────────────────────────────────
stop_services() {
    echo -e "${YELLOW}Stopping Docker Compose services...${NC}"
    docker compose down -v 2>/dev/null || true

    echo -e "${YELLOW}Deleting Minikube namespace...${NC}"
    kubectl delete namespace lang-agent 2>/dev/null || true

    echo -e "${GREEN}✅ All services stopped.${NC}"
}

# ─── Status Check ────────────────────────────────────────────────────────────
show_status() {
    echo -e "${BLUE}═══ Docker Compose Status ═══${NC}"
    docker compose ps 2>/dev/null || echo "  (not running)"

    echo ""
    echo -e "${BLUE}═══ Kubernetes Status ═══${NC}"
    kubectl get all -n lang-agent 2>/dev/null || echo "  (not running)"

    echo ""
    echo -e "${BLUE}═══ Resource Usage ═══${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null || true
}

# ─── Main ────────────────────────────────────────────────────────────────────
print_banner

case "${1}" in
    docker)
        deploy_docker
        ;;
    minikube)
        deploy_minikube
        ;;
    stop)
        stop_services
        ;;
    status)
        show_status
        ;;
    huawei)
        deploy_huawei
        ;;
    *)
        echo "Usage: $0 {docker|minikube|huawei|stop|status}"
        echo ""
        echo "  docker   - Build and deploy with Docker Compose"
        echo "  minikube - Deploy to local Minikube cluster"
        echo "  huawei   - Deploy to Huawei Cloud (SWR + CCE)"
        echo "  stop     - Stop all running services"
        echo "  status   - Show deployment status and resources"
        exit 1
        ;;
esac
