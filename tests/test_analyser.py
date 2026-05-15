"""Tests unitaires — pipeline d'analyse."""

import sys
from pathlib import Path

# Add parent directory to path so we can import core
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import ItemInput
from core.analyser import analyse_item
from core.utils import infer_brand, infer_category, demand_level


def test_infer_brand_from_marque():
    item = ItemInput(titre="Robe noire", description="", marque="Zara")
    assert infer_brand(item) == "Zara"


def test_infer_brand_from_title():
    item = ItemInput(titre="Veste Nike légère", description="")
    assert infer_brand(item).lower() == "nike"


def test_infer_category():
    item = ItemInput(titre="Jean slim bleu", description="jean slim taille 38")
    assert infer_category(item) == "jean"


def test_demand_level_high():
    assert demand_level("nike", "baskets") == "high demand"


def test_demand_level_mid():
    assert demand_level("h&m", "robe") == "mid demand"


def test_demand_level_low():
    assert demand_level("inconnu", "article mode") == "low/mid demand"


def test_analyse_item_complet():
    item = ItemInput(
        titre="Robe Zara noire taille M",
        description="Robe noire peu portée, taille M, matière légère, sans défaut.",
        prix_actuel=18.0,
        marque="Zara",
        etat="très bon état",
        images=["http://example.com/photo1.jpg", "http://example.com/photo2.jpg"],
    )
    result = analyse_item(item)
    assert len(result.optimisation_titres) == 3
    assert result.prix_recommandes["prix_recommande"] > 0
    assert 0 < result.score_global["score_global"] <= 10
    assert result.potentiel_vente != ""


if __name__ == "__main__":
    # Lancer les tests sans pytest
    tests = [
        test_infer_brand_from_marque,
        test_infer_brand_from_title,
        test_infer_category,
        test_demand_level_high,
        test_demand_level_mid,
        test_demand_level_low,
        test_analyse_item_complet,
    ]
    for t in tests:
        try:
            t()
            print(f"✅  {t.__name__}")
        except AssertionError as e:
            print(f"❌  {t.__name__} — {e}")

# Ajouter ces 2 tests à la fin du fichier existant

from core.html_parser import parse_items_html

def test_parse_html_table_basic():
    html = """
    <table>
      <tr><th>titre</th><th>prix</th><th>marque</th><th>état</th></tr>
      <tr><td>Robe Zara noire</td><td>18€</td><td>Zara</td><td>très bon état</td></tr>
      <tr><td>Jean Nike slim</td><td>25€</td><td>Nike</td><td>bon état</td></tr>
    </table>
    """
    items = parse_items_html(html)
    assert len(items) == 2
    assert items[0].titre == "Robe Zara noire"
    assert items[0].prix_actuel == 18.0
    assert items[1].marque == "Nike"


def test_parse_html_empty():
    items = parse_items_html("<html><body>Aucune donnée</body></html>")
    assert items == []