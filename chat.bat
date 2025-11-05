@echo off
REM Chat Service CLI - Colored output for Windows CMD

if "%~1"=="" (
    echo Usage: %0 "your question" [top_k]
    echo Example: %0 "What is MARP?" 5
    exit /b 1
)

set QUERY=%~1
set TOP_K=%~2
if "%TOP_K%"=="" set TOP_K=5

set CHAT_URL=http://localhost:8003/chat

REM Create JSON payload
set JSON_BODY={"query": "%QUERY%", "top_k": %TOP_K%}

REM Call API using PowerShell
powershell -NoProfile -Command ^
"$response = Invoke-RestMethod -Uri '%CHAT_URL%' -Method Post -ContentType 'application/json' -Body '%JSON_BODY%'; ^
if ($response.detail) { ^
    Write-Host 'Error: ' -ForegroundColor Red -NoNewline; ^
    Write-Host $response.detail -ForegroundColor White; ^
    exit 1 ^
} ^
Write-Host 'Query: ' -ForegroundColor Cyan -NoNewline; ^
Write-Host $response.query -ForegroundColor White; ^
Write-Host ''; ^
Write-Host 'Answer:' -ForegroundColor Cyan; ^
Write-Host $response.answer -ForegroundColor White; ^
Write-Host ''; ^
if ($response.citations) { ^
    Write-Host 'Citations:' -ForegroundColor Yellow; ^
    $i = 1; ^
    foreach ($cite in $response.citations) { ^
        Write-Host \"$i. \" -ForegroundColor Green -NoNewline; ^
        Write-Host $cite.title -ForegroundColor Magenta -NoNewline; ^
        Write-Host \" (Page \" -NoNewline; ^
        Write-Host $cite.page -ForegroundColor Yellow -NoNewline; ^
        Write-Host ')' -NoNewline; ^
        Write-Host \"`n   $($cite.url)\" -ForegroundColor DarkGray; ^
        $i++ ^
    } ^
} else { ^
    Write-Host 'Citations: No citations available' -ForegroundColor DarkGray ^
}"

if errorlevel 1 exit /b 1

