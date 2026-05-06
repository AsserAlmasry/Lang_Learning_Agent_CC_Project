# ==============================================================================
# deploy.ps1 - Windows PowerShell Deployment Script
# Language Learning Agent - Cloud Infrastructure
# ==============================================================================
# Usage:
#   .\deploy.ps1 docker     → Build & run with Docker Compose
#   .\deploy.ps1 minikube   → Deploy to local Minikube cluster
#   .\deploy.ps1 stop       → Stop all services
#   .\deploy.ps1 status     → Show running services status
# ==============================================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("docker", "minikube", "huawei", "stop", "status")]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [string]$CustomApiUrl = ""
)

$ErrorActionPreference = "Stop"

function Write-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║  🎓 Language Learning Agent - Deployment Automation        ║" -ForegroundColor Magenta
    Write-Host "║  Powered by: Asser Almasry | AI Engineer                   ║" -ForegroundColor Magenta
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

# ─── Docker Compose Deployment ───────────────────────────────────────────────
function Deploy-Docker {
    Write-Host "[1/4] Building Docker images..." -ForegroundColor Cyan
    docker compose build --no-cache

    Write-Host "[2/4] Starting services with resource limits..." -ForegroundColor Cyan
    docker compose up -d

    Write-Host "[3/4] Waiting for health checks..." -ForegroundColor Cyan
    Start-Sleep -Seconds 15

    Write-Host "[4/4] Verifying deployment..." -ForegroundColor Cyan
    docker compose ps

    Write-Host ""
    Write-Host "✅ Deployment Complete!" -ForegroundColor Green
    Write-Host "   🌐 Application:      http://localhost" -ForegroundColor Yellow
    Write-Host "   📊 Grafana Dashboard: http://localhost:3001" -ForegroundColor Yellow
    Write-Host "      Login: admin / avs5g962HaY2IpIJZgQvyg"
    Write-Host ""
    Write-Host "📈 Resource Usage:" -ForegroundColor Cyan
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
}

# ─── Minikube Deployment ─────────────────────────────────────────────────────
function Deploy-Minikube {
    Write-Host "[1/7] Starting Minikube cluster..." -ForegroundColor Cyan
    minikube start --cpus 4 --memory 10240 --driver=docker

    Write-Host "[2/7] Enabling NGINX Ingress addon..." -ForegroundColor Cyan
    minikube addons enable ingress
    minikube addons enable metrics-server

    Write-Host "[3/7] Switching to Minikube Docker daemon..." -ForegroundColor Cyan
    & minikube -p minikube docker-env --shell powershell | Invoke-Expression

    Write-Host "[4/7] Building images inside Minikube..." -ForegroundColor Cyan
    docker build -f Dockerfile.backend -t lang-agent/api-backend:latest .
    docker build -f Dockerfile.frontend -t lang-agent/frontend-ui:latest .

    Write-Host "[5/7] Applying Kubernetes manifests..." -ForegroundColor Cyan
    kubectl apply -f k8s/00-namespace.yaml
    kubectl apply -f k8s/01-secrets-configmap.yaml
    kubectl apply -f k8s/02-persistent-volumes.yaml
    kubectl apply -f k8s/03-backend-deployment.yaml
    kubectl apply -f k8s/04-frontend-deployment.yaml
    kubectl apply -f k8s/05-chromadb-statefulset.yaml
    kubectl apply -f k8s/06-ingress.yaml
    kubectl apply -f k8s/07-monitoring.yaml

    Write-Host "[6/7] Waiting for pods to become ready..." -ForegroundColor Cyan
    Start-Sleep -Seconds 30

    Write-Host "[7/7] Deployment status:" -ForegroundColor Cyan
    kubectl get all -n lang-agent

    $MINIKUBE_IP = minikube ip
    Write-Host ""
    Write-Host "✅ Minikube Deployment Complete!" -ForegroundColor Green
    Write-Host "   🌐 Application:      http://$MINIKUBE_IP" -ForegroundColor Yellow
    Write-Host "   📊 Grafana Dashboard: http://${MINIKUBE_IP}:31000" -ForegroundColor Yellow
    Write-Host "      Login: admin / avs5g962HaY2IpIJZgQvyg"
    Write-Host ""
    Write-Host "To access via tunnel: minikube tunnel" -ForegroundColor Cyan
    Write-Host "To view pod logs:     kubectl logs -f deploy/api-backend -n lang-agent" -ForegroundColor Cyan
    Write-Host "To view pod logs:     kubectl logs -f deploy/api-backend -n lang-agent" -ForegroundColor Cyan
    Write-Host "To check resources:   kubectl top pods -n lang-agent" -ForegroundColor Cyan
}

# ─── Huawei Cloud (ECS) Deployment ───────────────────────────────────────────
function Deploy-Huawei {
    $SWR_ENDPOINT = "swr.ap-southeast-3.myhuaweicloud.com" 
    $ORGANIZATION = "lang-agent-project"
    
    Write-Host "--- Huawei Cloud Deployment ---" -ForegroundColor Yellow
    Write-Host "Note: Ensure you have run 'docker login' for SWR." -ForegroundColor Gray
    
    Write-Host "[1/2] Building production images..." -ForegroundColor Cyan
    # Pass the Public IP or Custom URL so the Frontend knows where the Backend is
    $API_URL = if ($CustomApiUrl) { $CustomApiUrl } else { "https://lang-agent-asser.duckdns.org/api" }
    Write-Host "Targeting API: $API_URL" -ForegroundColor Yellow

    $API_KEY = (Select-String -Path ".env" -Pattern "API_SECRET_KEY=(.+)" | ForEach-Object { $_.Matches.Groups[1].Value })
    
    docker build --provenance=false -f Dockerfile.backend -t "${SWR_ENDPOINT}/${ORGANIZATION}/api-backend:v1" .
    docker build --provenance=false --build-arg "NEXT_PUBLIC_API_URL=$API_URL" --build-arg "NEXT_PUBLIC_API_KEY=$API_KEY" -f Dockerfile.frontend -t "${SWR_ENDPOINT}/${ORGANIZATION}/frontend-ui:v1" .

    Write-Host "[2/2] Pushing images to Huawei SWR..." -ForegroundColor Cyan
    docker push "${SWR_ENDPOINT}/${ORGANIZATION}/api-backend:v1"
    docker push "${SWR_ENDPOINT}/${ORGANIZATION}/frontend-ui:v1"

    Write-Host ""
    Write-Host "DONE: Images are now in the Cloud (SWR)!" -ForegroundColor Green
    Write-Host "Next Step: I will give you the command to pull these on your ECS server." -ForegroundColor Yellow
}


# ─── Stop All Services ───────────────────────────────────────────────────────
function Stop-Services {
    Write-Host "Stopping Docker Compose services..." -ForegroundColor Yellow
    docker compose down -v 2>$null

    Write-Host "Deleting Minikube namespace..." -ForegroundColor Yellow
    kubectl delete namespace lang-agent 2>$null

    Write-Host "✅ All services stopped." -ForegroundColor Green
}

# ─── Status Check ────────────────────────────────────────────────────────────
function Show-Status {
    Write-Host "═══ Docker Compose Status ═══" -ForegroundColor Cyan
    docker compose ps 2>$null

    Write-Host ""
    Write-Host "═══ Kubernetes Status ═══" -ForegroundColor Cyan
    kubectl get all -n lang-agent 2>$null

    Write-Host ""
    Write-Host "═══ Resource Usage ═══" -ForegroundColor Cyan
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>$null
}

# ─── Main ────────────────────────────────────────────────────────────────────
Write-Banner

switch ($Action) {
    "docker"   { Deploy-Docker }
    "minikube" { Deploy-Minikube }
    "stop"     { Stop-Services }
    "status"   { Show-Status }
    "huawei"   { Deploy-Huawei }
}

