# ============================================================
#  Unsloth 5060 Ti Starter — Bootstrap 1 lệnh
#  Chạy ở máy nhà (PowerShell):
#    irm https://raw.githubusercontent.com/sonhai88/unsloth-5060ti-starter/main/bootstrap.ps1 | iex
#  Nó tự: clone repo -> cài Unsloth Studio -> in hướng dẫn.
# ============================================================
$ErrorActionPreference = "Stop"

$repo = "https://github.com/sonhai88/unsloth-5060ti-starter.git"
$dest = Join-Path $env:USERPROFILE "unsloth-5060ti-starter"

Write-Host ""
Write-Host "  === Unsloth 5060 Ti Starter ===" -ForegroundColor Green
Write-Host ""

# 1) Cần git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "  [X] Chưa có Git. Cài tại https://git-scm.com/download/win rồi chạy lại." -ForegroundColor Red
    return
}

# 2) Cảnh báo driver (Blackwell cần driver mới)
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    Write-Host "  [i] GPU phát hiện được:" -ForegroundColor DarkGray
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>$null | ForEach-Object { Write-Host "      $_" -ForegroundColor DarkGray }
} else {
    Write-Host "  [!] Không thấy nvidia-smi — kiểm tra đã cài driver NVIDIA mới chưa (Blackwell cần driver mới)." -ForegroundColor Yellow
}

# 3) Clone (hoặc cập nhật nếu đã có)
if (Test-Path $dest) {
    Write-Host "  [i] Đã có $dest — đang cập nhật..." -ForegroundColor DarkGray
    git -C $dest pull --ff-only
} else {
    Write-Host "  [1/2] Clone repo về $dest ..." -ForegroundColor Cyan
    git clone --depth 1 $repo $dest
}

# 4) Cài Unsloth Studio (installer chính hãng — tự lo torch/CUDA 12.8/Triton)
Write-Host ""
Write-Host "  [2/2] Cài Unsloth Studio (lần đầu tải vài GB, kiên nhẫn)..." -ForegroundColor Cyan
Write-Host ""
irm https://unsloth.ai/install.ps1 | iex

# 5) Xong
Write-Host ""
Write-Host "  ============================================================" -ForegroundColor Green
Write-Host "  XONG!" -ForegroundColor Green
Write-Host "    - Tìm icon 'Unsloth Studio' trên Desktop -> double-click." -ForegroundColor Green
Write-Host "    - Trình duyệt tự mở app (hoặc vào http://localhost:8888)." -ForegroundColor Green
Write-Host "    - Repo (train.py, data, Modelfile) ở: $dest" -ForegroundColor Green
Write-Host "    - Hướng dẫn: $dest\studio\QUICKSTART.md" -ForegroundColor Green
Write-Host "  ============================================================" -ForegroundColor Green
Write-Host ""
