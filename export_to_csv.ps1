# Script para exportar datos de SQL Server a CSV
# Requiere: SQL Server, bcp utility instalado

$ServerName = "DESKTOP-CCBH45L"
$DatabaseName = "BI_Prueba"
$OutputDir = "data"

# Crear directorio data si no existe
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    Write-Host "✅ Directorio 'data' creado" -ForegroundColor Green
}

Write-Host "`n🚀 Iniciando exportación de datos..." -ForegroundColor Cyan
Write-Host "Servidor: $ServerName" -ForegroundColor Yellow
Write-Host "Base de datos: $DatabaseName" -ForegroundColor Yellow
Write-Host "Destino: $OutputDir\" -ForegroundColor Yellow
Write-Host ""

# Tablas a exportar
$tables = @(
    "customers",
    "stores", 
    "products",
    "orders",
    "order_items",
    "returns"
)

$totalTables = $tables.Count
$currentTable = 0

foreach ($table in $tables) {
    $currentTable++
    $outputFile = "$OutputDir\$table.csv"
    
    Write-Host "[$currentTable/$totalTables] Exportando $table..." -NoNewline
    
    try {
        # Usar bcp (Bulk Copy Program) para exportar
        # -c: character data type
        # -t,: comma delimiter  
        # -r\n: row terminator
        # -S: server name
        # -T: trusted connection (Windows Auth)
        # -o: output file for messages
        
        $query = "SELECT * FROM $table"
        $bcpCommand = "bcp `"$DatabaseName.dbo.$table`" out `"$outputFile`" -c -t, -r\n -S $ServerName -T -C UTF8"
        
        # Ejecutar bcp y capturar resultado
        $result = Invoke-Expression $bcpCommand 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            # Contar líneas del archivo
            $lineCount = (Get-Content $outputFile | Measure-Object -Line).Lines
            Write-Host " ✅ ($lineCount registros)" -ForegroundColor Green
        } else {
            Write-Host " ❌ Error" -ForegroundColor Red
            Write-Host "Detalles: $result" -ForegroundColor Red
        }
    }
    catch {
        Write-Host " ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n📊 Resumen de archivos exportados:" -ForegroundColor Cyan
Write-Host ""

Get-ChildItem "$OutputDir\*.csv" | ForEach-Object {
    $lines = (Get-Content $_.FullName | Measure-Object -Line).Lines
    $size = [math]::Round($_.Length / 1KB, 2)
    Write-Host "  📄 $($_.Name.PadRight(20)) - $($lines.ToString().PadLeft(6)) líneas - $size KB" -ForegroundColor White
}

$totalSize = [math]::Round((Get-ChildItem "$OutputDir\*.csv" | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
Write-Host "`n  💾 Tamaño total: $totalSize MB" -ForegroundColor Yellow

Write-Host "`n✅ Exportación completada exitosamente!" -ForegroundColor Green
Write-Host "📁 Archivos disponibles en: $(Resolve-Path $OutputDir)" -ForegroundColor Cyan
