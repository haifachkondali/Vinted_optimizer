#!/bin/bash
# Quick start script for Vinted Optimizer on Linux/Mac/WSL

echo "Vinted Optimizer - Installation rapide"
echo "======================================="
echo ""

# Create virtual environment
echo "[1/4] Creation de l'environnement virtuel..."
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "[2/4] Installation des dependances..."
pip install --upgrade pip
pip install -r requirements.txt

# Run tests
echo "[3/4] Verification des tests..."
pytest tests/ -v

# Show usage
echo ""
echo "[4/4] Installation terminee !"
echo ""
echo "Utilisation rapide:"
echo "  # Mode scraping"
echo "  python main.py --user ton_pseudo"
echo ""
echo "  # Mode fichier JSON"
echo "  python main.py --file mon_article.json"
echo ""
echo "  # Mode export RGPD"
echo "  python main.py --export-zip vinted_export.zip"
echo ""
echo "Voir README.md pour plus de details."
