# ============================================================================
# Script PowerShell para exportar datos de SQL Server a CSV para PostgreSQL
# ============================================================================

$serverInstance = "DESKTOP-CCBH45L"
$database = "BI_Prueba"
$outputPath = "c:\temp"

Write-Host "=======================" -ForegroundColor Cyan
Write-Host "Exportación SQL → CSV" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan
Write-Host ""

# Crear directorio si no existe
New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

# Lista de tablas a exportar
$tables = @("customers", "stores", "products", "orders", "order_items", "returns")

foreach ($table in $tables) {
    $outputFile = "$outputPath\$table.csv"
    $query = "SELECT * FROM $table"
    
    Write-Host "Exportando $table..." -ForegroundColor Yellow
    
    # Usar sqlcmd para exportar a CSV
    sqlcmd -S $serverInstance -d $database -Q $query -s "," -W -o $outputFile
    
    if (Test-Path $outputFile) {
        $lines = (Get-Content $outputFile | Measure-Object -Line).Lines
        Write-Host "✓ $table exportado: $lines líneas" -ForegroundColor Green
    } else {
        Write-Host "✗ Error exportando $table" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=======================" -ForegroundColor Cyan
Write-Host "Exportación completada" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan
Write-Host "Archivos en: $outputPath" -ForegroundColor White
Write-Host ""
Write-Host "Siguiente paso: Cargar CSVs a PostgreSQL en Render" -ForegroundColor Magenta
Write-Host "Ver: dashboard_web/README.md para instrucciones" -ForegroundColor Magenta
