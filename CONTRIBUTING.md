# Guide de contribution

Merci de vouloir contribuer a Vinted Optimizer !

## Installation de developpement

```bash
# Clone le repo
git clone <repo-url>
cd vinted_optimizer

# Crée un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate      # Windows

# Installe les dependances (dev + test)
pip install -r requirements.txt
pip install -e .
pip install pytest black flake8 mypy
```

## Tests

Avant de faire une PR :

```bash
# Lance les tests
pytest tests/

# Formate le code
black core/ main.py

# Verifie la syntaxe
flake8 core/ main.py
mypy core/ main.py
```

## Conventions

- Docstrings en anglais pour les modules importants
- Type hints pour toutes les fonctions publiques
- Pas d'accents speciaux ou emojis (encodage ASCII-safe)
- Messages de commit en anglais ou francais (coherent)

## Structure de PR

1. Un commit par feature/fix
2. Description claire de ce qui est change
3. Tests unitaires pour les nouvelles fonctionnalites
4. README mis a jour si necessaire
