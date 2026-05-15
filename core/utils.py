from __future__ import annotations
import re
from typing import List
from .models import ItemInput
from .constants import STOPWORDS, HIGH_DEMAND, MID_DEMAND, CATEGORY_MAP


def clean_text(text: str) -> str:
    """Remove extra whitespace from text.
    
    Args:
        text: Raw text input
        
    Returns:
        Cleaned text with normalized whitespace
    """
    return re.sub(r"\s+", " ", (text or "").strip())


def extract_keywords(*parts: str, limit: int = 10) -> List[str]:
    """Extract unique keywords from text parts.
    
    Args:
        *parts: Text parts to extract keywords from
        limit: Maximum number of keywords to return
        
    Returns:
        List of unique keywords (longest first)
    """
    tokens = []
    for part in parts:
        for tok in re.findall(r"[A-Za-zA-Za-z0-9'&-]+", (part or "").lower()):
            if len(tok) < 3 or tok in STOPWORDS:
                continue
            tokens.append(tok)
    seen: List[str] = []
    for tok in tokens:
        if tok not in seen:
            seen.append(tok)
    return seen[:limit]


def infer_brand(item: ItemInput) -> str:
    """Infer brand name from item data.
    
    Args:
        item: ItemInput object
        
    Returns:
        Brand name (title case) or 'Sans marque' if not found
    """
    if item.marque:
        return item.marque.strip().title()
    title = item.titre.lower()
    for brand in sorted(HIGH_DEMAND | MID_DEMAND, key=len, reverse=True):
        if brand in title:
            return brand.title()
    return "Sans marque"


def infer_category(item: ItemInput) -> str:
    """Infer product category from item data.
    
    Args:
        item: ItemInput object
        
    Returns:
        Category name from mapping or 'article mode' if not found
    """
    if item.categorie:
        return item.categorie
    text = f"{item.titre} {item.description}".lower()
    for key, value in CATEGORY_MAP.items():
        if key in text:
            return value
    return "article mode"


def demand_level(brand: str, category: str) -> str:
    """Determine market demand level for item.
    
    Args:
        brand: Brand name (lowercase)
        category: Product category
        
    Returns:
        One of 'high demand', 'mid demand', or 'low/mid demand'
    """
    b = brand.lower()
    if b in HIGH_DEMAND or "vintage" in category.lower():
        return "high demand"
    if b in MID_DEMAND:
        return "mid demand"
    return "low/mid demand"