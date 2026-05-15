# 🛍️ Vinted Optimizer

Agent IA local pour optimiser automatiquement tes annonces Vinted.
Scrape ton profil public, analyse chaque article et génère des rapports complets.

---

## Installation

```bash
# 1. Clone ou crée le dossier
cd vinted-optimizer

# 2. Crée un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate        # Linux/Mac/WSL
.venv\Scripts\activate           # Windows

# 3. Installe les dépendances
pip install -r requirements.txt
```

## Utilisation

### Mode scraping automatique (via pseudo Vinted)
```bash
python main.py --user TON_PSEUDO_VINTED
python main.py --user TON_PSEUDO_VINTED --max 30 --delay 2.0
```

### Mode fichier JSON (si scraping bloqué)
```bash
python main.py --file input_vinted.json
```

### Options complètes
| Option | Description | Défaut |
|---|---|---|
| `--user` | Pseudo Vinted | — |
| `--file` | Fichier JSON d'entrée | — |
| `--max` | Nombre max d'articles | 20 |
| `--delay` | Délai entre requêtes (s) | 1.5 |
| `--country` | Pays Vinted (fr/be/es/de) | fr |
| `--output` | Dossier de sortie | output_vinted/ |

## Format du fichier JSON (mode --file)

```json
[
  {
    "titre": "Robe Zara noire taille M",
    "description": "Robe peu portée, sans défaut, taille M.",
    "prix_actuel": 18.0,
    "marque": "Zara",
    "etat": "très bon état",
    "images": []
  }
]
```

## Lancer les tests

```bash
python tests/test_analyser.py
# ou avec pytest :
pip install pytest && pytest tests/
```

## Structure des résultats

Chaque rapport `output_vinted/analyse_001.md` contient :
1. Résumé article
2. Diagnostic
3. Problèmes majeurs
4. 3 titres optimisés SEO
5. Nouvelle description
6. Prix recommandé / vente rapide / minimum
7. Analyse photo
8. Stratégie marketing + hashtags + timing
9. Score global /10
10. Potentiel de vente

## ⚠️ Avertissements
- Le scraping lit uniquement les annonces **publiques** — aucun mot de passe requis.
- En cas de blocage Vinted, augmenter `--delay` à 3.0 ou 5.0.
- Conforme à une utilisation personnelle, mais contre les CGU Vinted en usage automatisé massif.
## Mode export RGPD Vinted (HTML)

Vinted permet de télécharger toutes tes données personnelles :
**Paramètres → Confidentialité → Gérer les données du compte → Faire la demande**

Tu recevras un email avec un lien pour télécharger un fichier `.zip`.

### Utilisation avec le ZIP (méthode la plus simple)
```bash
python main.py --export-zip ./vinted_export.zip
```

### Utilisation avec le dossier décompressé
```bash
# Décompresse le ZIP d'abord, puis :
python main.py --export-folder ./vinted_data/
```

Le programme détecte automatiquement le bon fichier HTML dans le dossier
et extrait toutes tes annonces pour les analyser.