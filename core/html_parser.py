"""
Parseur de l'export RGPD Vinted (ZIP ou dossier décompressé).
Structure attendue :
    vinted_data/
    ├── items/index.html          ← tes annonces
    ├── transactions/index.html   ← tes ventes
    ├── messages/index.html       ← tes conversations
    └── ...
"""

from __future__ import annotations
import re
import zipfile
from pathlib import Path
from typing import List, Optional
from html.parser import HTMLParser

from .models import ItemInput


# ─── Parser HTML générique ────────────────────────────────────
class TableParser(HTMLParser):
    """Extrait les lignes d'un tableau HTML sous forme de dicts."""

    def __init__(self):
        super().__init__()
        self.headers: List[str] = []
        self.rows: List[dict] = []
        self._in_th = False
        self._in_td = False
        self._current_row: List[str] = []
        self._cell_data = ""
        self._in_table = False

    def handle_starttag(self, tag, attrs):
        if tag == "table": self._in_table = True
        if tag == "th":    self._in_th = True;  self._cell_data = ""
        if tag == "td":    self._in_td = True;  self._cell_data = ""
        if tag == "tr" and self._in_table:
            self._current_row = []

    def handle_endtag(self, tag):
        if tag == "th":
            self.headers.append(self._cell_data.strip())
            self._in_th = False
        if tag == "td":
            self._current_row.append(self._cell_data.strip())
            self._in_td = False
        if tag == "tr" and self._current_row:
            if self.headers and len(self._current_row) == len(self.headers):
                self.rows.append(dict(zip(self.headers, self._current_row)))
        if tag == "table":
            self._in_table = False

    def handle_data(self, data):
        if self._in_th or self._in_td:
            self._cell_data += data


def _parse_html_table(html_content: str) -> List[dict]:
    parser = TableParser()
    parser.feed(html_content)
    return parser.rows


def _safe_float(val: str) -> Optional[float]:
    try:
        return float(re.sub(r"[^\d.,]", "", val).replace(",", "."))
    except (ValueError, AttributeError):
        return None


def _safe_int(val: str) -> Optional[int]:
    try:
        return int(re.sub(r"[^\d]", "", val))
    except (ValueError, AttributeError):
        return None


# ─── Recherche flexible d'une colonne ─────────────────────────
def _find_col(row: dict, *candidates: str) -> str:
    for key in row:
        for c in candidates:
            if c.lower() in key.lower():
                return row[key]
    return ""


# ─── Parseur items/annonces ───────────────────────────────────
def parse_items_html(html_content: str) -> List[ItemInput]:
    """Parse items from Vinted GDPR export HTML (microdata + img format)."""
    from html import unescape

    items = []

    # Split by cell divs
    cells = re.findall(
        r'<div class="cell" itemscope>.*?(?=<div class="cell" itemscope>|$)',
        html_content, re.DOTALL
    )

    for cell in cells:
        item_data: dict = {}

        # ── Titre depuis cell-header ──────────────────────────
        title_match = re.search(r'<div class="cell-header"[^>]*>([^<]+)</div>', cell)
        if title_match:
            item_data['title'] = unescape(title_match.group(1).strip())

        # ── Propriétés itemprop (description, brand, status…) ─
        prop_matches = re.findall(
            r'<span itemprop="([^"]+)">([^<]+)</span>',
            cell
        )
        for prop, value in prop_matches:
            item_data[prop] = unescape(value.strip())

        # ── Photos : toutes les <img> dans la cellule ─────────
        img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', cell)
        # Filtrer les icônes/logos (trop petites URLs génériques)
        images = [
            unescape(src) for src in img_srcs
            if not any(skip in src.lower() for skip in [
                'logo', 'icon', 'avatar', 'sprite', 'flag', 'badge',
                'placeholder', '1x1', 'pixel'
            ])
        ]
        item_data['images'] = images

        # ── Ne garder que si on a un titre ───────────────────
        if item_data.get('title'):
            prix = _safe_float(item_data.get('order_value', '') or item_data.get('price', ''))
            items.append(ItemInput(
                titre       = item_data.get('title', ''),
                description = item_data.get('description', ''),
                prix_actuel = prix,
                marque      = item_data.get('brand') or None,
                etat        = item_data.get('status') or None,
                categorie   = item_data.get('category') or None,
                images      = item_data.get('images', []),
            ))

    # ── Fallback tableau HTML si microdata vide ────────────────
    if not items:
        rows = _parse_html_table(html_content)
        for row in rows:
            titre = (
                _find_col(row, "titre", "title", "nom", "article", "annonce")
                or _find_col(row, "item")
            )
            if not titre:
                continue
            items.append(ItemInput(
                titre       = titre,
                description = _find_col(row, "description", "desc", "détail"),
                prix_actuel = _safe_float(_find_col(row, "prix", "price", "montant", "tarif")),
                marque      = _find_col(row, "marque", "brand") or None,
                etat        = _find_col(row, "état", "etat", "condition", "statut") or None,
                categorie   = _find_col(row, "catégorie", "categorie", "type") or None,
                images      = [],
            ))

    return items


# ─── Chargement depuis dossier ou ZIP ─────────────────────────
def _read_html(path: Path) -> str:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return ""


def _find_items_html(root: Path) -> Optional[Path]:
    """Cherche le bon index.html dans le dossier d'export."""
    candidates = [
        "items", "annonces", "articles", "catalog",
        "listings", "products", "mes_annonces"
    ]
    for name in candidates:
        p = root / name / "index.html"
        if p.exists():
            return p
    all_html = list(root.rglob("index.html"))
    if all_html:
        return max(all_html, key=lambda p: p.stat().st_size)
    return None


def load_from_export_folder(folder: Path) -> List[ItemInput]:
    """Load items from an extracted Vinted GDPR export folder."""
    html_path = _find_items_html(folder)
    if not html_path:
        print(f"[WARN] Aucun fichier HTML trouvé dans {folder}")
        return []
    print(f"[INFO] Fichier annonces trouvé : {html_path}")
    html = _read_html(html_path)
    items = parse_items_html(html)
    print(f"[OK] {len(items)} article(s) extrait(s) de l'export HTML.")
    return items


def load_from_zip(zip_path: Path, extract_to: Optional[Path] = None) -> List[ItemInput]:
    """Load items directly from a Vinted GDPR export ZIP file."""
    if extract_to is None:
        extract_to = zip_path.parent / zip_path.stem

    print(f"[INFO] Décompression de {zip_path.name} -> {extract_to}")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_to)

    return load_from_export_folder(extract_to)
