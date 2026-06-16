# ============================================================
#  Unsloth 5060 Ti Starter — Bootstrap 1 lệnh
#  Chạy ở máy nhà (PowerShell):
#    [Net.ServicePointManager]::SecurityProtocol='Tls12'; irm https://raw.githubusercontent.com/sonhai88/unsloth-5060ti-starter/main/bootstrap.ps1 | iex
#  Nó tự: clone repo -> cài Unsloth Studio (process con) -> in hướng dẫn.
# ============================================================
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

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
    Write-Host "  [i] GPU:" -ForegroundColor DarkGray
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>$null | ForEach-Object { Write-Host "      $_" -ForegroundColor DarkGray }
} else {
    Write-Host "  [!] Không thấy nvidia-smi — kiểm tra driver NVIDIA mới chưa (Blackwell cần driver mới)." -ForegroundColor Yellow
}

# 3) Clone (hoặc cập nhật). Xử cả trường hợp thư mục tồn tại nhưng KHÔNG phải git repo.
try {
    if (Test-Path (Join-Path $dest ".git")) {
        Write-Host "  [i] Đã có repo ở $dest — đang cập nhật..." -ForegroundColor DarkGray
        git -C $dest pull --ff-only
    } else {
        if (Test-Path $dest) {
            Write-Host "  [!] $dest tồn tại nhưng không phải git repo — đổi tên thành .bak..." -ForegroundColor Yellow
            Rename-Item $dest "$dest.bak-$(Get-Random)" -ErrorAction SilentlyContinue
        }
        Write-Host "  [1/2] Clone repo về $dest ..." -ForegroundColor Cyan
        git clone --depth 1 $repo $dest
    }
} catch {
    Write-Host "  [X] Clone/cập nhật lỗi: $($_.Exception.Message)" -ForegroundColor Red
    return
}
if (-not (Test-Path (Join-Path $dest ".git"))) {
    Write-Host "  [X] Clone không thành công, dừng lại." -ForegroundColor Red
    return
}

# 4) Cài Unsloth Studio trong PROCESS CON.
#    Lý do: installer chính hãng gọi `exit` ở top-level; nếu chạy lồng iex
#    nó sẽ ĐÓNG cửa sổ PowerShell của anh (mất cả thông báo bên dưới).
#    Process con cô lập `exit` đó, bootstrap vẫn chạy tiếp.
Write-Host ""
Write-Host "  [2/2] Cài Unsloth Studio (lần đầu tải vài GB, kiên nhẫn)..." -ForegroundColor Cyan
Write-Host ""
$installCmd = "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; irm https://unsloth.ai/install.ps1 | iex"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -Command $installCmd
$ok = ($LASTEXITCODE -eq 0)

# 5) Tổng kết (trung thực theo kết quả cài)
Write-Host ""
if ($ok) {
    Write-Host "  ============================================================" -ForegroundColor Green
    Write-Host "  XONG!" -ForegroundColor Green
    Write-Host "    - Tìm icon 'Unsloth Studio' trên Desktop -> double-click." -ForegroundColor Green
    Write-Host "    - Trình duyệt tự mở app (hoặc vào http://localhost:8888)." -ForegroundColor Green
    Write-Host "    - Repo (train.py, data, Modelfile): $dest" -ForegroundColor Green
    Write-Host "    - Hướng dẫn: $dest\studio\QUICKSTART.md" -ForegroundColor Green
    Write-Host "  ============================================================" -ForegroundColor Green
} else {
    Write-Host "  [X] Cài Studio gặp lỗi (exit code $LASTEXITCODE)." -ForegroundColor Red
    Write-Host "      Hay gặp nhất: driver NVIDIA cũ (lỗi sm_120) -> update driver rồi chạy lại." -ForegroundColor Yellow
    Write-Host "      Repo vẫn đã clone ở: $dest — xem $dest\studio\QUICKSTART.md" -ForegroundColor Yellow
}
Write-Host ""
