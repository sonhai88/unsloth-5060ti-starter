@echo off
REM ============================================================
REM  Cai Unsloth Studio (chay 1 lan duy nhat)
REM  Double-click file nay. Sau khi xong:
REM    -> Co icon "Unsloth Studio" tren Desktop, double-click la chay.
REM ============================================================
echo.
echo   Dang cai Unsloth Studio... (lan dau tai vai GB, kien nhan)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; irm https://unsloth.ai/install.ps1 | iex"
echo.
echo   ============================================================
echo   Xong! Tim icon "Unsloth Studio" tren Desktop -> double-click.
echo   Trinh duyet se tu mo http://localhost (app cua anh).
echo   ============================================================
echo.
pause
