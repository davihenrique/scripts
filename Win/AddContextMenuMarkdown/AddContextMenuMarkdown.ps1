# Adiciona "Novo > Documento Markdown" ao menu de contexto do Windows
# Execute como Administrador

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
    Write-Error "Execute este script como Administrador."
    exit 1
}

# Cria arquivo modelo em ShellNew
$templateDir = "C:\Windows\ShellNew"
$templateFile = "$templateDir\query.sql"

if (-not (Test-Path $templateDir)) {
    New-Item -ItemType Directory -Path $templateDir -Force | Out-Null
}

Set-Content -Path $templateFile -Value "" -Encoding UTF8

# Monta o drive HKCR se ainda nao existir
if (-not (Get-PSDrive -Name HKCR -ErrorAction SilentlyContinue)) {
    New-PSDrive -PSProvider Registry -Name HKCR -Root HKEY_CLASSES_ROOT | Out-Null
}

# Registra a extensao .md (preserva valor existente se houver)
$mdKey = "HKCR:\.sql"
if (-not (Test-Path $mdKey)) {
    New-Item -Path $mdKey -Force | Out-Null
}

$currentDefault = (Get-ItemProperty -Path $mdKey -Name "(Default)" -ErrorAction SilentlyContinue)."(Default)"
if (-not $currentDefault) {
    Set-ItemProperty -Path $mdKey -Name "(Default)" -Value "sql.query"
    $currentDefault = "sql.query"
}

# Registra o tipo de arquivo com nome amigavel
$typeKey = "HKCR:\$currentDefault"
if (-not (Test-Path $typeKey)) {
    New-Item -Path $typeKey -Force | Out-Null
}
Set-ItemProperty -Path $typeKey -Name "(Default)" -Value "Nova Query SQL"

# Adiciona a chave ShellNew para aparecer no menu Novo
$shellNewKey = "$mdKey\ShellNew"
if (-not (Test-Path $shellNewKey)) {
    New-Item -Path $shellNewKey -Force | Out-Null
}
Set-ItemProperty -Path $shellNewKey -Name "FileName" -Value $templateFile

Write-Host "Pronto! Abra o Explorador de Arquivos, clique com o direito e va em Novo > Documento Markdown." -ForegroundColor Green
Write-Host "Se a opcao nao aparecer imediatamente, reinicie o Explorer (taskkill /f /im explorer.exe && start explorer)." -ForegroundColor Yellow
