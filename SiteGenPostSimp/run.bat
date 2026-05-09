@echo off
chcp 65001 >nul 2>&1

REM Установка переменных окружения
set PROXY_API_KEY=sk-Wn6aMngfsrbCRtoN30ILHSfNFLVJR1mp
set VK_ACCESS_TOKEN=vk1.a.2NvfRcVFmHQezpBl1oCTviVmSaPlnTT3g7m0l4IC0U5RqwGYLb_LzdJla-9L7ATbC-mR7YrTfoyrbc11_vBM_NjrfFRFpit7FqYNOSfIEhzSkcHZjYyvwZBM0OgYsrdUY4y-Svk9gc7rmpuUEHUXBra8T2fK_T2XsCacfA5h4j6H4vTYs0IiJ8lR_KSGefyP28BV8GP0MIYIojTQQGML4Q
set VK_GROUP_ID=238535077

cd /d "%~dp0"
python app.py
pause
