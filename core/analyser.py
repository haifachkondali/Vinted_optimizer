from __future__ import annotations
from typing import Dict, Any, List, Optional
from .models import ItemInput, AnalysisOutput
from .constants import STATE_BOOST, HIGH_DEMAND, MID_DEMAND
from .utils import clean_text, extract_keywords, infer_brand, infer_category, demand_level

from .gemini_client import (
    gemini_rewrite_description,
    gemini_build_titles,
    gemini_available,
)


# ─── Scoring attractivité ──────────────────────────────────────
def attractiveness_score(item: ItemInput, brand: str, category: str) -> float:
    """Score d'attractivité 0–10 basé sur marque, prix, état, description, photos."""
    score = 4.5
    b = brand.lower()
    if b in HIGH_DEMAND:   score += 1.6
    elif b in MID_DEMAND:  score += 0.8

    if item.prix_actuel is not None:
        if item.prix_actuel <= 10:   score += 1.4
        elif item.prix_actuel <= 20: score += 1.1
        elif item.prix_actuel <= 35: score += 0.8
        elif item.prix_actuel <= 60: score += 0.3

    score += STATE_BOOST.get((item.etat or "").lower(), 0.0)

    desc_len = len(clean_text(item.description))
    if desc_len > 200:   score += 0.8
    elif desc_len > 100: score += 0.5
    elif desc_len > 50:  score += 0.2

    nb_photos = len(item.images)
    if nb_photos >= 5:   score += 1.0
    elif nb_photos >= 3: score += 0.7
    elif nb_photos >= 1: score += 0.3

    return round(min(score, 9.8), 1)


# ─── Potentiel de revente ──────────────────────────────────────
def resale_potential(level: str, score: float) -> str:
    if level == "high demand" and score >= 7.5: return "Fort"
    if score >= 6.0: return "Moyen"
    return "Faible à moyen"


# ─── Titres SEO (fallback sans Gemini) ────────────────────────
def build_titles(item: ItemInput, brand: str, category: str) -> List[str]:
    """3 titres optimisés SEO Vinted : marque + catégorie + état + détail."""
    etat   = item.etat or "très bon état"
    kws    = extract_keywords(item.titre, item.description, limit=4)
    detail = kws[0].title() if kws else ""

    # Cherche taille dans le titre/description
    taille_match = None
    import re
    for text in [item.titre, item.description]:
        m = re.search(r'\b(XS|S|M|L|XL|XXL|\d{2,3})\b', text or "", re.IGNORECASE)
        if m:
            taille_match = m.group(1).upper()
            break

    taille_str = f"taille {taille_match}" if taille_match else ""

    t1 = clean_text(f"{brand} {category.title()} {detail} {etat} {taille_str}").strip()[:80]
    t2 = clean_text(f"{brand} {category.title()} {taille_str} {etat} — livraison rapide").strip()[:80]
    t3 = clean_text(f"{category.title()} {brand} {detail} {taille_str} {etat}").strip()[:80]
    return [t1, t2, t3]


# ─── Description (fallback sans Gemini) ───────────────────────
def rewrite_description(item: ItemInput, brand: str, category: str) -> str:
    """Description Vinted professionnelle, accent correct, ton vendeur."""
    etat    = item.etat or "très bon état"
    kw      = ", ".join(extract_keywords(item.titre, item.description, limit=5))
    details = clean_text(item.description) if item.description else "Matière, taille et mesures à compléter."

    return (
        f"✨ {brand} {category} en {etat} — prêt(e) à être porté(e) !\n\n"
        f"📌 Points clés :\n"
        f"  • Marque {brand}, qualité reconnue\n"
        f"  • État : {etat}, soigné(e) et propre\n"
        f"  • Photos authentiques, sans filtre\n\n"
        f"📝 Détails : {details}\n\n"
        f"🔍 Mots-clés : {kw if kw else category}\n\n"
        f"📦 Envoi rapide & soigné · Paiement 100 % sécurisé via Vinted\n"
        f"💬 N'hésitez pas à faire une offre ou poser vos questions !"
    )


# ─── Stratégie prix ───────────────────────────────────────────
def pricing_strategy(item: ItemInput, level: str) -> Dict[str, Any]:
    """Prix recommandés selon demande marché, état et catégorie."""
    base = item.prix_actuel if item.prix_actuel is not None else 20.0

    # Multiplicateur selon demande
    if level == "high demand":  mult = 1.10
    elif level == "mid demand": mult = 1.02
    else:                       mult = 0.92

    # Ajustement selon état
    etat_lower = (item.etat or "").lower()
    if "neuf" in etat_lower:          mult += 0.08
    elif "très bon" in etat_lower:    mult += 0.03
    elif "satisfaisant" in etat_lower: mult -= 0.05

    optimal   = round(base * mult, 2)
    rapide    = round(optimal * 0.85, 2)
    minimum   = round(optimal * 0.70, 2)

    # Justification lisible
    if level == "high demand":
        just = f"Marque très demandée sur Vinted — vous pouvez vous positionner légèrement au-dessus du marché."
    elif level == "mid demand":
        just = f"Marque correcte — restez dans la moyenne du marché pour maximiser les vues."
    else:
        just = f"Marque peu recherchée — prix compétitif indispensable pour déclencher la vente."

    return {
        "prix_recommande":            optimal,
        "prix_vente_rapide":          rapide,
        "prix_minimum_acceptable":    minimum,
        "justification":              just,
    }


# ─── Analyse photos ───────────────────────────────────────────
def photo_analysis(item: ItemInput) -> Dict[str, Any]:
    """Évalue la couverture photo et fournit des recommandations concrètes."""
    n = len(item.images)

    if n == 0:
        return {
            "score": 1.5,
            "nb_photos": 0,
            "diagnostic": "❌ Aucune photo détectée — frein majeur à la conversion (-60 % de vues en moyenne).",
            "corrections": [
                "📸 Ajouter au minimum 4 photos pour maximiser les vues.",
                "🌅 Utiliser la lumière naturelle d'une fenêtre (sans flash).",
                "🎨 Fond uni blanc, beige ou gris clair uniquement.",
                "📐 Photo 1 : article entier à plat ou sur cintre.",
                "🔍 Photo 2 : zoom sur la matière / texture.",
                "🏷️  Photo 3 : étiquette marque + composition.",
                "⚠️  Photo 4 : défaut visible le cas échéant (gage de confiance).",
            ]
        }
    elif n < 3:
        score = 3.5
        diag  = f"⚠️  Seulement {n} photo(s) — insuffisant, les acheteurs hésitent sous 3 photos."
        corrections = [
            "Ajouter au moins 2 photos supplémentaires.",
            "Zoom matière et étiquette manquants.",
            "Vérifier l'éclairage : lumière naturelle recommandée.",
        ]
    elif n < 5:
        score = 6.0
        diag  = f"✅ {n} photos — correct mais perfectible."
        corrections = [
            "Ajouter un zoom sur l'étiquette ou la composition.",
            "Une photo portée (sur mannequin ou sur soi) augmente les conversions de 30 %.",
        ]
    else:
        score = min(7.5 + (n - 5) * 0.2, 9.5)
        diag  = f"🌟 {n} photos — excellent ! Couverture visuelle complète."
        corrections = [
            "Vérifier la cohérence lumière/fond sur toutes les photos.",
        ]

    return {
        "score":       round(score, 1),
        "nb_photos":   n,
        "diagnostic":  diag,
        "corrections": corrections,
    }


# ─── Stratégie marketing ──────────────────────────────────────
def marketing_strategy(item: ItemInput, brand: str, category: str) -> Dict[str, Any]:
    kws      = extract_keywords(item.titre, item.description, brand, category, limit=10)
    hashtags = [f"#{k.replace(' ', '').replace(chr(39), '')}" for k in kws[:6]]
    return {
        "mots_cles_tendance":       kws,
        "hashtags_vinted":          hashtags,
        "timing_publication":       "🕕 Publier entre 18h–22h en semaine, ou dimanche 15h–20h (pics d'activité Vinted FR).",
        "suggestions_bundles":      f"💼 Créer un lot : même marque ({brand}), même taille ou même style — augmente le panier moyen.",
        "optimisation_visibilite":  (
            "🔄 Relancer avec nouvelles photos + baisse de 5–10 % du prix toutes les 10 jours.\n"
            "⭐ Utiliser la fonction 'Mettre en avant' Vinted aux heures de pointe.\n"
            "💬 Répondre vite aux messages — le taux de réponse influence la visibilité."
        ),
    }


# ─── Score global ─────────────────────────────────────────────
def compute_global_score(
    attract: float,
    photo_score: float,
    titre: str,
    prix: Optional[float]
) -> Dict[str, Any]:
    # SEO titre
    titre_clean = clean_text(titre)
    if len(titre_clean) >= 30:   seo = 8.5
    elif len(titre_clean) >= 15: seo = 6.5
    else:                         seo = 4.0

    # Score pricing
    pricing = 7.5 if prix is not None else 4.5

    conversion = round((attract + seo + pricing + photo_score) / 4, 1)
    global_score = round((attract + photo_score + seo + pricing + conversion) / 5, 1)

    return {
        "attractivite":        attract,
        "qualite_photo":       photo_score,
        "seo":                 seo,
        "pricing":             pricing,
        "potentiel_conversion": conversion,
        "score_global":        global_score,
    }


# ─── Label potentiel de vente ─────────────────────────────────
def sales_potential_label(score: float) -> str:
    if score >= 7.5: return "🟢 Bon potentiel — vente rapide si photos et prix alignés."
    if score >= 6.0: return "🟡 Potentiel correct — optimiser titre, visuels ou prix."
    return "🔴 Potentiel limité — travail prioritaire avant relance."


# ─── Point d'entrée principal ─────────────────────────────────
def analyse_item(item: ItemInput, use_ai: bool = True) -> AnalysisOutput:
    brand    = infer_brand(item)
    category = infer_category(item)
    level    = demand_level(brand, category)
    attract  = attractiveness_score(item, brand, category)

    # Titres : Gemini en priorité, fallback template
    titles = None
    if use_ai and gemini_available():
        titles = gemini_build_titles(item, brand, category)
    if not titles:
        titles = build_titles(item, brand, category)

    # Description : Gemini en priorité, fallback template
    desc = None
    if use_ai and gemini_available():
        desc = gemini_rewrite_description(item, brand, category)
    if not desc:
        desc = rewrite_description(item, brand, category)

    prices    = pricing_strategy(item, level)
    photos    = photo_analysis(item)
    marketing = marketing_strategy(item, brand, category)
    scores    = compute_global_score(attract, photos["score"], item.titre, item.prix_actuel)

    # Problèmes détectés
    problems = []
    titre_len = len(clean_text(item.titre))
    desc_len  = len(clean_text(item.description))

    if titre_len < 15:
        problems.append("⚠️  Titre trop court — ajouter marque, taille, couleur et état pour le SEO Vinted.")
    elif titre_len < 25:
        problems.append("💡 Titre perfectible — intégrer la taille et l'état pour plus de visibilité.")

    if desc_len < 50:
        problems.append("❌ Description trop courte — préciser matière, taille, dimensions et défauts éventuels.")
    elif desc_len < 120:
        problems.append("💡 Description à enrichir : matière, entretien, mesures exactes.")

    if photos["nb_photos"] == 0:
        problems.append("❌ Aucune photo — sans photo, l'annonce est invisible dans les résultats.")
    elif photos["nb_photos"] < 3:
        problems.append(f"⚠️  Seulement {photos['nb_photos']} photo(s) — ajouter zoom matière + étiquette.")

    if item.prix_actuel is None:
        problems.append("❓ Prix non détecté — vérifier et renseigner manuellement.")
    elif item.prix_actuel < 3:
        problems.append("💡 Prix très bas — vérifier que les frais Vinted n'annulent pas le bénéfice.")

    if item.marque is None and item.etat is None:
        problems.append("ℹ️  Marque et état non renseignés — informations essentielles pour les acheteurs.")

    if not problems:
        problems.append("✅ Base saine — gains possibles via packaging annonce et micro-ajustements prix.")

    return AnalysisOutput(
        resume_article       = f"{brand} {category}, demande {level}, attractivité {attract}/10.",
        diagnostic           = (
            f"Article {category}. Positionnement marché : {level}. "
            f"Potentiel revente : {resale_potential(level, attract).lower()}."
        ),
        problemes_majeurs    = problems,
        optimisation_titres  = titles,
        nouvelle_description = desc,
        prix_recommandes     = prices,
        analyse_photo        = photos,
        strategie_marketing  = marketing,
        score_global         = scores,
        potentiel_vente      = sales_potential_label(scores["score_global"]),
    )
