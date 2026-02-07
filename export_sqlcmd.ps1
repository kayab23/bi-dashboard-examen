# Script alternativo para exportar datos usando sqlcmd
# Más simple y compatible con PowerShell

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
Write-Host ""

# Tablas a exportar con sus queries
$exports = @(
    @{Table="customers"; Query="SELECT * FROM customers"},
    @{Table="stores"; Query="SELECT * FROM stores"},
    @{Table="products"; Query="SELECT * FROM products"},
    @{Table="orders"; Query="SELECT * FROM orders"},
    @{Table="order_items"; Query="SELECT * FROM order_items"},
    @{Table="returns"; Query="SELECT * FROM returns"}
)

$totalTables = $exports.Count
$currentTable = 0

foreach ($export in $exports) {
    $currentTable++
    $tableName = $export.Table
    $query = $export.Query
    $outputFile = "$OutputDir\$tableName.csv"
    
    Write-Host "[$currentTable/$totalTables] Exportando $tableName..." -NoNewline
    
    try {
        # Crear query SQL que genera CSV
        $sqlQuery = @"
SET NOCOUNT ON;
$query
"@
        
        # Ejecutar con sqlcmd y guardar a archivo
        # -S: servidor
        # -d: base de datos
        # -E: autenticación Windows
        # -s,: delimitador de columna (coma)
        # -W: quitar espacios en blanco al final
        # -h-1: sin headers (los agregamos manualmente después)
        
        $tempFile = "$OutputDir\$tableName`_temp.csv"
        
        # Primero obtener los headers
        $headersQuery = @"
SELECT TOP 1 * FROM $tableName;
"@
        
        $headers = sqlcmd -S $ServerName -d $DatabaseName -E -Q $headersQuery -s "," -W -h-1 | Select-Object -First 1
        
        # Luego obtener los datos
        sqlcmd -S $ServerName -d $DatabaseName -E -Q $sqlQuery -s "," -W -h-1 -o $tempFile
        
        # Combinar headers + datos
        if (Test-Path $tempFile) {
            $headers | Out-File -FilePath $outputFile -Encoding UTF8
            Get-Content $tempFile | Out-File -FilePath $outputFile -Encoding UTF8 -Append
            Remove-Item $tempFile
            
            $lineCount = (Get-Content $outputFile | Measure-Object -Line).Lines - 1
            Write-Host " ✅ ($lineCount registros)" -ForegroundColor Green
        } else {
            Write-Host " ❌ Error al crear archivo" -ForegroundColor Red
        }
    }
    catch {
        Write-Host " ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n📊 Resumen de archivos exportados:" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "$OutputDir\*.csv") {
    Get-ChildItem "$OutputDir\*.csv" | ForEach-Object {
        $lines = (Get-Content $_.FullName | Measure-Object -Line).Lines - 1
        $size = [math]::Round($_.Length / 1KB, 2)
        Write-Host "  📄 $($_.Name.PadRight(20)) - $($lines.ToString().PadLeft(6)) registros - $size KB" -ForegroundColor White
    }
    
    $totalSize = [math]::Round((Get-ChildItem "$OutputDir\*.csv" | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
    Write-Host "`n  💾 Tamaño total: $totalSize MB" -ForegroundColor Yellow
    Write-Host "`n✅ Exportación completada!" -ForegroundColor Green
} else {
    Write-Host "  ❌ No se generaron archivos CSV" -ForegroundColor Red
}

Write-Host "`n📁 Archivos disponibles en: $(Resolve-Path $OutputDir)" -ForegroundColor Cyan
