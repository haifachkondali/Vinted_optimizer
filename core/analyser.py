from __future__ import annotations
from typing import Dict, Any, List, Optional
from .models import ItemInput, AnalysisOutput
from .constants import STATE_BOOST, HIGH_DEMAND, MID_DEMAND
from .utils import clean_text, extract_keywords, infer_brand, infer_category, demand_level


def attractiveness_score(item: ItemInput, brand: str, category: str) -> float:
    """Calculate item attractiveness score (0-10).
    
    Considers brand popularity, price, condition, description length, and photos.
    """
    score = 4.5
    b = brand.lower()
    if b in HIGH_DEMAND:   score += 1.6
    elif b in MID_DEMAND:  score += 0.8
    if item.prix_actuel is not None:
        if item.prix_actuel <= 15:   score += 1.2
        elif item.prix_actuel <= 30: score += 0.8
        elif item.prix_actuel <= 60: score += 0.3
    score += STATE_BOOST.get((item.etat or "").lower(), 0.0)
    if len(clean_text(item.description)) > 120: score += 0.6
    if item.images: score += 0.8
    return round(min(score, 9.8), 1)


def resale_potential(level: str, score: float) -> str:
    """Determine resale potential label based on demand level and score."""
    if level == "high demand" and score >= 7: return "Fort"
    if score >= 5.8: return "Moyen"
    return "Faible a moyen"


def build_titles(item: ItemInput, brand: str, category: str) -> List[str]:
    """Generate 3 optimized title suggestions for better SEO."""
    etat = item.etat or "tres bon etat"
    kws = extract_keywords(item.titre, item.description, limit=4)
    strong = kws[0].title() if kws else category.title()
    return [
        clean_text(f"{brand} {category.title()} {strong} {etat}")[:100],
        clean_text(f"{brand} {category.title()} tendance {etat}")[:100],
        clean_text(f"{brand} {strong} {category.title()} {etat}")[:100],
    ]


def rewrite_description(item: ItemInput, brand: str, category: str) -> str:
    """Generate optimized product description template.
    
    Args:
        item: ItemInput object
        brand: Brand name
        category: Product category
        
    Returns:
        Formatted description text ready for Vinted
    """
    etat = item.etat or "tres bon etat"
    kw = ", ".join(extract_keywords(item.titre, item.description, limit=6))
    details = clean_text(item.description) if item.description else "Informations a completer : matiere, taille, mesures."
    return (
        f"Shine {brand} {category} en {etat}, pret(e) a etre porte(e) immediatement.\n\n"
        f"- Coupe facile a associer au quotidien\n"
        f"- Article soigne, photos authentiques sans filtre\n"
        f"- Mots-cles utiles : {kw if kw else category}\n\n"
        f"Details : {details}\n\n"
        f"Envoi rapide [envoi] Paiement securise via Vinted. N'hesitez pas a faire une offre !"
    )


def pricing_strategy(item: ItemInput, level: str) -> Dict[str, Any]:
    """Generate pricing recommendations based on market demand.
    
    Args:
        item: ItemInput object with current price
        level: Demand level (high/mid/low)
        
    Returns:
        Dict with recommended prices and justification
    """
    base = item.prix_actuel if item.prix_actuel is not None else 20.0
    if level == "high demand":   optimal = round(base * 1.08, 2)
    elif level == "mid demand":  optimal = round(base * 1.00, 2)
    else:                        optimal = round(base * 0.92, 2)
    return {
        "prix_recommande": optimal,
        "prix_vente_rapide": round(optimal * 0.85, 2),
        "prix_minimum_acceptable": round(optimal * 0.72, 2),
        "justification": (
            "Prix optimal calcule selon la demande marche. "
            "Prix vente rapide pour declencher plus de clics. "
            "Minimum pour ne pas devaloriser l'article."
        ),
    }


def photo_analysis(item: ItemInput) -> Dict[str, Any]:
    """Analyze photo count and quality.
    
    Args:
        item: ItemInput object
        
    Returns:
        Dict with score, diagnostics, and improvement suggestions
    """
    n = len(item.images)
    if n == 0:
        return {
            "score": 3.5, "nb_photos": 0,
            "diagnostic": "Aucune photo detectee - gros frein a la conversion.",
            "corrections": [
                "Ajouter au minimum 3 photos.",
                "Utiliser la lumiere naturelle d'une fenetre.",
                "Fond uni blanc ou beige.",
                "Photo 1 : article entier. Photo 2 : detail matiere. Photo 3 : etiquette / defaut."
            ]
        }
    score = min(3.5 + n * 0.8, 8.5)
    return {
        "score": round(score, 1), "nb_photos": n,
        "diagnostic": f"{n} photo(s) detectee(s). Analyse qualitative manuelle recommandee.",
        "corrections": [
            "Lumiere naturelle proche d'une fenetre.",
            "Ajouter un zoom matiere + etiquette.",
            "Fond neutre sans distractions.",
        ]
    }


def marketing_strategy(item: ItemInput, brand: str, category: str) -> Dict[str, Any]:
    kws = extract_keywords(item.titre, item.description, brand, category, limit=10)
    hashtags = [f"#{k.replace(' ','').replace(chr(39),'')}" for k in kws[:6]]
    return {
        "mots_cles_tendance": kws,
        "hashtags_vinted": hashtags,
        "timing_publication": "Publier entre 18h et 22h en semaine, ou dimanche 15h–20h.",
        "suggestions_bundles": f"Créer un lot : même marque ({brand}), même taille ou même style.",
        "optimisation_visibilite": (
            "Relancer avec nouvelles photos + baisse de 5–10% du prix toutes les 10 jours. "
            "Utiliser la fonction 'Mettre en avant' Vinted aux heures de pointe."
        ),
    }


def compute_global_score(attract: float, photo_score: float, titre: str, prix: Optional[float]) -> Dict[str, Any]:
    seo = 7.5 if len(clean_text(titre)) >= 10 else 5.5
    pricing = 7.0 if prix is not None else 5.5
    conversion = round((attract + seo + pricing + photo_score) / 4, 1)
    return {
        "attractivite": attract,
        "qualite_photo": photo_score,
        "seo": seo,
        "pricing": pricing,
        "potentiel_conversion": conversion,
        "score_global": round((attract + photo_score + seo + pricing + conversion) / 5, 1),
    }


def sales_potential_label(score: float) -> str:
    if score >= 7.5: return "🟢 Bon potentiel — vente rapide si photos et prix alignés."
    if score >= 6.0: return "🟡 Potentiel correct — optimiser titre, visuels ou prix."
    return "🔴 Potentiel limité — travail prioritaire avant relance."


def analyse_item(item: ItemInput) -> AnalysisOutput:
    brand    = infer_brand(item)
    category = infer_category(item)
    level    = demand_level(brand, category)
    attract  = attractiveness_score(item, brand, category)
    titles   = build_titles(item, brand, category)
    desc     = rewrite_description(item, brand, category)
    prices   = pricing_strategy(item, level)
    photos   = photo_analysis(item)
    marketing = marketing_strategy(item, brand, category)
    scores   = compute_global_score(attract, photos["score"], item.titre, item.prix_actuel)

    problems = []
    if len(clean_text(item.titre)) < 15:
        problems.append("Titre trop court pour le SEO Vinted.")
    if len(clean_text(item.description)) < 80:
        problems.append("Description trop courte : ajouter matière, taille, défauts éventuels.")
    if photos["nb_photos"] < 3:
        problems.append(f"Seulement {photos['nb_photos']} photo(s) — objectif minimum : 3.")
    if item.prix_actuel is None:
        problems.append("Prix non détecté — vérifier et renseigner manuellement.")
    if not problems:
        problems.append("Base saine — gains possibles via packaging annonce et micro-ajustements prix.")

    return AnalysisOutput(
        resume_article  = f"{brand} {category}, demande {level}, attractivité {attract}/10.",
        diagnostic      = (
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