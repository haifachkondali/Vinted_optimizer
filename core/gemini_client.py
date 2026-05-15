"""
Client Gemini AI — génère titres et descriptions optimisées.
Clé API gratuite sur : https://aistudio.google.com/app/apikey
"""

from __future__ import annotations
import os
from typing import List, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .models import ItemInput


def _get_client() -> Optional[object]:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or not GEMINI_AVAILABLE:
        return None
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-1.5-flash")


def gemini_rewrite_description(
    item: ItemInput,
    brand: str,
    category: str,
) -> Optional[str]:
    """
    Génère une description Vinted optimisée via Gemini.
    Retourne None si Gemini n'est pas disponible ou si erreur.
    """
    model = _get_client()
    if not model:
        return None

    prompt = f"""
Tu es un expert en vente de vêtements sur Vinted.
Rédige une description de vente accrocheuse, courte (max 180 mots), 
naturelle et honnête pour cet article :

- Marque : {brand}
- Catégorie : {category}
- État : {item.etat or 'non précisé'}
- Prix : {item.prix_actuel or 'non précisé'} €
- Titre actuel : {item.titre}
- Description actuelle : {item.description or 'aucune'}

Règles :
1. Commence par un emoji accrocheur
2. Mets en valeur la marque et l'état
3. Ajoute 3-4 mots-clés tendance Vinted naturellement intégrés
4. Termine par une invitation à faire une offre
5. Ton conversationnel, pas robotique
6. Uniquement en français
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️  Gemini erreur description : {e}")
        return None


def gemini_build_titles(
    item: ItemInput,
    brand: str,
    category: str,
) -> Optional[List[str]]:
    """
    Génère 3 titres SEO optimisés via Gemini.
    Retourne None si Gemini n'est pas disponible.
    """
    model = _get_client()
    if not model:
        return None

    prompt = f"""
Tu es un expert SEO pour Vinted.
Génère exactement 3 titres d'annonce optimisés pour cet article.

- Marque : {brand}
- Catégorie : {category}
- État : {item.etat or 'non précisé'}
- Titre actuel : {item.titre}
- Description : {item.description or 'aucune'}

Règles :
1. Maximum 80 caractères par titre
2. Inclure : marque + type vêtement + état + 1 mot-clé tendance
3. Pas de majuscules excessives
4. Varier les formulations
5. Format de réponse : une ligne par titre, sans numérotation ni tiret
"""
    try:
        response = model.generate_content(prompt)
        lines = [l.strip() for l in response.text.strip().splitlines() if l.strip()]
        return lines[:3] if lines else None
    except Exception as e:
        print(f"⚠️  Gemini erreur titres : {e}")
        return None


def gemini_available() -> bool:
    """Vérifie si Gemini est configuré et utilisable."""
    return bool(os.getenv("GEMINI_API_KEY", "").strip()) and GEMINI_AVAILABLE