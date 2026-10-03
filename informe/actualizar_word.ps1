# Abre un .docx en Word, actualiza la tabla de contenidos, guarda y exporta un PDF de revision
# (el PDF va a %TEMP%\revision para no chocar con archivos abiertos por el usuario).
# Uso: powershell -File informe\actualizar_word.ps1 C:\ruta\documento.docx
$Archivo = ([string]$args[0]).Replace('/', '\')
$dir = Join-Path $env:TEMP 'revision'
if (-not (Test-Path $dir)) { New-Item -ItemType Directory $dir | Out-Null }
$pdf = Join-Path $dir ([IO.Path]::GetFileNameWithoutExtension($Archivo) + '.pdf')
$w = New-Object -ComObject Word.Application
$w.DisplayAlerts = 0
try {
  $d = $w.Documents.Open($Archivo)
  for ($i = 1; $i -le $d.TablesOfContents.Count; $i++) { $d.TablesOfContents.Item($i).Update() }
  $d.Save()
  $d.ExportAsFixedFormat($pdf, 17)
  (Split-Path $Archivo -Leaf) + ': ' + $d.ComputeStatistics(2) + ' paginas'
  $d.Close($false)
} catch { 'ERROR: ' + $_.Exception.Message } finally { $w.Quit() }
