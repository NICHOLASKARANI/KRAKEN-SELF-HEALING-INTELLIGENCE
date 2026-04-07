param([string]$Command = "help")

switch ($Command) {
    "start" {
        Write-Host "Starting KRAKEN..." -ForegroundColor Green
        docker-compose up -d
        Start-Sleep -Seconds 5
        Write-Host "KRAKEN started! Access Grafana at http://localhost:3000" -ForegroundColor Green
    }
    "stop" {
        Write-Host "Stopping KRAKEN..." -ForegroundColor Yellow
        docker-compose down
        Write-Host "KRAKEN stopped" -ForegroundColor Green
    }
    "status" {
        docker ps --format "table {{.Names}}\t{{.Status}}"
    }
    "logs" {
        docker-compose logs -f ai-brain
    }
    "dashboard" {
        Start-Process "http://localhost:3000"
    }
    "api" {
        Start-Process "http://localhost:8000/docs"
    }
    default {
        Write-Host "KRAKEN Commands:" -ForegroundColor Cyan
        Write-Host "  .\manage.ps1 start     - Start all services"
        Write-Host "  .\manage.ps1 stop      - Stop all services"
        Write-Host "  .\manage.ps1 status    - Check status"
        Write-Host "  .\manage.ps1 logs      - View AI logs"
        Write-Host "  .\manage.ps1 dashboard - Open Grafana"
        Write-Host "  .\manage.ps1 api       - Open AI Brain API"
    }
}
