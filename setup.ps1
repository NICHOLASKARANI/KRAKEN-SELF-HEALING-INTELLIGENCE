# setup.ps1 - Windows PowerShell script for KRAKEN
Write-Host "🦑 KRAKEN - Self-Healing Intelligence Core" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
$dockerCheck = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCheck) {
    Write-Host "❌ Docker is required but not installed." -ForegroundColor Red
    Write-Host "Download Docker Desktop from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Host "After installing, restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker info > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not running"
    }
} catch {
    Write-Host "❌ Docker Desktop is not running." -ForegroundColor Red
    Write-Host "Please start Docker Desktop from your Start Menu and try again." -ForegroundColor Yellow
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path logs,data | Out-Null

# Check for OpenAI API key
if (-not $env:OPENAI_API_KEY) {
    Write-Host "⚠️  OpenAI API key not set" -ForegroundColor Yellow
    $env:OPENAI_API_KEY = Read-Host "Please enter your OpenAI API key"
    [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $env:OPENAI_API_KEY, "User")
}

# Build and start services
Write-Host "🚀 Building and starting KRAKEN..." -ForegroundColor Green
docker-compose up -d --build

# Wait for services
Write-Host "⏳ Waiting for services to be ready (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check health
Write-Host "🔍 Checking system health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ AI Brain is operational" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  AI Brain may still be starting. Check with: docker logs kraken-brain" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 KRAKEN is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "Access points:" -ForegroundColor Cyan
Write-Host "  📊 Grafana Dashboard: http://localhost:3000 (admin/kraken123)"
Write-Host "  🤖 AI Brain API: http://localhost:8000/docs"
Write-Host "  📈 Prometheus: http://localhost:9090"
Write-Host "  🔍 Kibana: http://localhost:5601"
Write-Host ""
Write-Host "To view the React dashboard, open dashboard/frontend/index.html in your browser" -ForegroundColor Yellow
Write-Host ""
Write-Host "Run '.\manage.ps1 help' for more commands" -ForegroundColor Cyan