@echo off
REM Quick start script for Vinted Optimizer on Windows

echo Vinted Optimizer - Installation rapide
echo =======================================
echo.

REM Create virtual environment
echo [1/4] Creation de l'environnement virtuel...
python -m venv .venv
call .venv\Scripts\activate.bat

REM Install dependencies
echo [2/4] Installation des dependances...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Run tests
echo [3/4] Verification des tests...
pytest tests/ -v

REM Show usage
echo.
echo [4/4] Installation terminee !
echo.
echo Utilisation rapide:
echo   # Mode scraping
echo   python main.py --user ton_pseudo
echo.
echo   # Mode fichier JSON
echo   python main.py --file mon_article.json
echo.
echo   # Mode export RGPD
echo   python main.py --export-zip vinted_export.zip
echo.
echo Voir README.md pour plus de details.
pause
