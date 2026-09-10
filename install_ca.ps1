# install_ca.ps1 - Cài đặt SmartLogis Root CA vào Windows Trusted Store
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CaPath = Join-Path $ScriptDir "certbot\conf\smartlogis_root_ca.crt"

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "     SMARTLOGIS AI - CAI DAT CHUNG CHI SSL TRUSTED ROOT CA VAO WINDOWS" -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Cyan

if (-not (Test-Path $CaPath)) {
    Write-Host "[1/2] Chua co file CA. Dang sinh chung chi..." -ForegroundColor Yellow
    $pyScript = Join-Path $ScriptDir "scripts\generate_trusted_ssl_ca.py"
    if (Test-Path "$ScriptDir\venv\Scripts\python.exe") {
        & "$ScriptDir\venv\Scripts\python.exe" $pyScript
    } else {
        & py -3.12 $pyScript
    }
}

Write-Host "[1/2] Dang them chung chi vao Windows Trusted Root Certification Authorities..." -ForegroundColor Yellow

try {
    $cert = Import-Certificate -FilePath $CaPath -CertStoreLocation "Cert:\LocalMachine\Root"
    Write-Host ""
    Write-Host "===============================================================================" -ForegroundColor Green
    Write-Host " [THANH CONG 100%] DA CAI DAT CHUNG CHI BAO MAT VAO HE THONG WINDOWS!" -ForegroundColor Green
    Write-Host "===============================================================================" -ForegroundColor Green
    Write-Host " * Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
    Write-Host " * Subject   : $($cert.Subject)" -ForegroundColor Gray
    Write-Host ""
    Write-Host " Ket qua: Trinh duyet Chrome, Edge, Coc Coc se nhan dien domain:" -ForegroundColor White
    Write-Host "     https://smartlogis-ai.com" -ForegroundColor Cyan
    Write-Host " la BẢO MẬT TUYỆT ĐỐI (Co bieu tuong o khoa an toan, KHONG CON CANH BAO)." -ForegroundColor Green
    Write-Host ""
    Write-Host " Huong dan:" -ForegroundColor White
    Write-Host "  1. Dong tat ca cac cua so Chrome hien tai roi mo lai (hoac mo Tab An danh moi)." -ForegroundColor Gray
    Write-Host "  2. Truy cap: https://smartlogis-ai.com" -ForegroundColor Cyan
    Write-Host "===============================================================================" -ForegroundColor Green
} catch {
    Write-Host "[LOI] Khong the cai dat chung chi: $_" -ForegroundColor Red
    Write-Host "Vui long dam bao chay voi quyen Administrator." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Nhan phim Enter de dong cua so..." -ForegroundColor Gray
[void][System.Console]::ReadLine()
