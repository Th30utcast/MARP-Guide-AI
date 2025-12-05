# Chat Service CLI - Colored output for Windows PowerShell

param(
    [Parameter(Mandatory=$true)]
    [string]$Query,

    [Parameter(Mandatory=$false)]
    [int]$TopK = 5
)

$ChatUrl = "http://localhost:8003/chat"

try {
    $body = @{
        query = $Query
        top_k = $TopK
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri $ChatUrl -Method Post -ContentType "application/json" -Body $body

    if ($response.detail) {
        Write-Host "❌ Error: " -ForegroundColor Red -NoNewline
        Write-Host $response.detail -ForegroundColor White
        exit 1
    }

    # Query
    Write-Host "🔍 Query: " -ForegroundColor Cyan -NoNewline
    Write-Host $response.query -ForegroundColor White
    Write-Host ""

    # Answer
    Write-Host "📝 Answer:" -ForegroundColor Cyan
    Write-Host $response.answer -ForegroundColor White
    Write-Host ""

    # Citations
    if ($response.citations -and $response.citations.Count -gt 0) {
        Write-Host "📚 Citations:" -ForegroundColor Yellow
        $counter = 1
        foreach ($cite in $response.citations) {
            Write-Host "$counter. " -ForegroundColor Green -NoNewline
            Write-Host $cite.title -ForegroundColor Magenta -NoNewline
            Write-Host " (Page " -NoNewline
            Write-Host $cite.page -ForegroundColor Yellow -NoNewline
            Write-Host ")"
            Write-Host "   $($cite.url)" -ForegroundColor DarkGray
            $counter++
        }
    } else {
        Write-Host "📚 Citations: " -ForegroundColor Yellow -NoNewline
        Write-Host "No citations available" -ForegroundColor DarkGray
    }

} catch {
    Write-Host "❌ Error: " -ForegroundColor Red -NoNewline
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        try {
            $errorJson = $responseBody | ConvertFrom-Json
            Write-Host $errorJson.detail -ForegroundColor White
        } catch {
            Write-Host $responseBody -ForegroundColor White
        }
    } else {
        Write-Host $_.Exception.Message -ForegroundColor White
    }
    Write-Host ""
    Write-Host "Tip: Run 'docker compose ps' to check service status" -ForegroundColor DarkGray
    exit 1
}
