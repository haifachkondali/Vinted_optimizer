.PHONY: help install test run format lint clean

help:
	@echo "Vinted Optimizer - Commandes disponibles:"
	@echo "  make install  - Installe les dependances"
	@echo "  make test     - Lance les tests"
	@echo "  make run      - Lance l'app (exemple)"
	@echo "  make format   - Formate le code (black)"
	@echo "  make lint     - Verifie le code (flake8)"
	@echo "  make clean    - Nettoie les fichiers generes"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt pytest black flake8 mypy

test:
	pytest tests/ -v --tb=short

run:
	python main.py --help

format:
	black core/ main.py tests/

lint:
	flake8 core/ main.py tests/
	mypy core/ --ignore-missing-imports

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache build dist *.egg-info
	rm -rf output_vinted/
