# PowerShell script to enable Docker BuildKit
# Run this before building: .\enable-buildkit.ps1

Write-Host "Enabling Docker BuildKit for this session..." -ForegroundColor Green

$env:DOCKER_BUILDKIT=1
$env:COMPOSE_DOCKER_CLI_BUILD=1

Write-Host "✓ DOCKER_BUILDKIT=1" -ForegroundColor Green
Write-Host "✓ COMPOSE_DOCKER_CLI_BUILD=1" -ForegroundColor Green
Write-Host ""
Write-Host "BuildKit is now enabled for this PowerShell session." -ForegroundColor Cyan
Write-Host "You can now run: docker compose build --build" -ForegroundColor Cyan
Write-Host ""
Write-Host "To make this permanent, add these to your system environment variables:" -ForegroundColor Yellow
Write-Host "  DOCKER_BUILDKIT = 1" -ForegroundColor Yellow
Write-Host "  COMPOSE_DOCKER_CLI_BUILD = 1" -ForegroundColor Yellow
