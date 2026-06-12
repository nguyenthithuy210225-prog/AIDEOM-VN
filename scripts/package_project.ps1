$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$zip = Join-Path $root "aideom_vn_submission.zip"
$stage = Join-Path $env:TEMP "aideom_vn_submission_stage"

if (Test-Path $zip) {
    Remove-Item -LiteralPath $zip -Force
}

if (Test-Path $stage) {
    Remove-Item -LiteralPath $stage -Recurse -Force
}
New-Item -ItemType Directory -Path $stage | Out-Null

$items = @(
    "dashboard",
    "data",
    "notebooks",
    "src",
    "tests",
    "outputs",
    "scripts",
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "run_app.bat",
    "package_app.bat"
)

$items | ForEach-Object {
    $source = Join-Path $root $_
    if (Test-Path $source) {
        Copy-Item -LiteralPath $source -Destination $stage -Recurse -Force
    }
}

$reportsSource = Join-Path $root "reports"
$reportsTarget = Join-Path $stage "reports"
New-Item -ItemType Directory -Path $reportsTarget | Out-Null
$reportItems = @(
    "README.md",
    "BAO_CAO_BAO_VE_AIDEOM_VN.docx",
    "BAO_CAO_CUOI_KY_DRAFT.md",
    "BAO_CAO_TOM_TAT_AIDEOM_VN.md",
    "HUONG_DAN_SU_DUNG_WEB_APP.md"
)
$reportItems | ForEach-Object {
    $source = Join-Path $reportsSource $_
    if (Test-Path $source) {
        Copy-Item -LiteralPath $source -Destination $reportsTarget -Force
    }
}

Get-ChildItem -LiteralPath $stage -Recurse -Directory -Force |
    Where-Object { $_.Name -in @("__pycache__", ".pytest_cache", ".ipynb_checkpoints", ".streamlit", "web_exports") } |
    Remove-Item -Recurse -Force

Get-ChildItem -LiteralPath $stage -Recurse -File -Force |
    Where-Object { $_.Extension -in @(".pyc", ".pyo", ".log", ".tmp", ".bak") } |
    Remove-Item -Force

$paths = Get-ChildItem -LiteralPath $stage -Force
Compress-Archive -Path $paths.FullName -DestinationPath $zip -Force
Remove-Item -LiteralPath $stage -Recurse -Force
Write-Host "Created $zip"
