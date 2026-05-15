from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ItemInput:
    titre: str
    description: str
    prix_actuel: Optional[float] = None
    marque: Optional[str] = None
    etat: Optional[str] = None
    categorie: Optional[str] = None
    vues: Optional[int] = None
    favoris: Optional[int] = None
    messages: Optional[int] = None
    images: List[str] = field(default_factory=list)
    url: Optional[str] = None


@dataclass
class AnalysisOutput:
    resume_article: str
    diagnostic: str
    problemes_majeurs: List[str]
    optimisation_titres: List[str]
    nouvelle_description: str
    prix_recommandes: Dict[str, Any]
    analyse_photo: Dict[str, Any]
    strategie_marketing: Dict[str, Any]
    score_global: Dict[str, Any]
    potentiel_vente: str