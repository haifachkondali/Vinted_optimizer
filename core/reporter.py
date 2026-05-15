from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Tuple
from .models import ItemInput, AnalysisOutput


def format_report(item: ItemInput, result: AnalysisOutput) -> str:
    """Format analysis result as a markdown report.
    
    Args:
        item: Input item details
        result: Analysis output
        
    Returns:
        Formatted markdown report as string
    """
    p  = result.prix_recommandes
    ph = result.analyse_photo
    m  = result.strategie_marketing
    s  = result.score_global
    lines = [
        "# Analyse annonce Vinted",
        f"**URL source :** {item.url or 'N/A'}",
        "",
        "## 1. Resume article", result.resume_article, "",
        "## 2. Diagnostic", result.diagnostic, "",
        "## 3. Problemes majeurs",
        *[f"- {x}" for x in result.problemes_majeurs], "",
        "## 4. Optimisation titre (x3)",
        *[f"- {x}" for x in result.optimisation_titres], "",
        "## 5. Nouvelle description",
        result.nouvelle_description, "",
        "## 6. Prix recommandes",
        f"- Prix recommande : **{p['prix_recommande']} EUR**",
        f"- Prix vente rapide : {p['prix_vente_rapide']} EUR",
        f"- Prix minimum acceptable : {p['prix_minimum_acceptable']} EUR",
        f"- Justification : {p['justification']}", "",
        "## 7. Analyse photo",
        f"- Score photo : {ph['score']}/10 ({ph['nb_photos']} photo(s))",
        f"- Diagnostic : {ph['diagnostic']}",
        *[f"- Correction : {c}" for c in ph["corrections"]], "",
        "## 8. Strategie marketing",
        f"- Mots-cles : {', '.join(m['mots_cles_tendance']) or 'N/A'}",
        f"- Hashtags : {' '.join(m['hashtags_vinted']) or 'N/A'}",
        f"- Timing : {m['timing_publication']}",
        f"- Bundles : {m['suggestions_bundles']}",
        f"- Visibilite : {m['optimisation_visibilite']}", "",
        "## 9. Score global",
        f"- Attractivite     : {s['attractivite']}/10",
        f"- Qualite photo    : {s['qualite_photo']}/10",
        f"- SEO titre        : {s['seo']}/10",
        f"- Pricing          : {s['pricing']}/10",
        f"- Conversion       : {s['potentiel_conversion']}/10",
        f"- **Score global   : {s['score_global']}/10**", "",
        "## 10. Potentiel de vente",
        result.potentiel_vente,
    ]
    return "\n".join(lines)


def save_reports(pairs: List[Tuple[ItemInput, AnalysisOutput]], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    all_data = []
    for idx, (item, result) in enumerate(pairs, start=1):
        (output_dir / f"analyse_{idx:03d}.md").write_text(format_report(item, result), encoding="utf-8")
        all_data.append({"input": asdict(item), "output": asdict(result)})
    json_path = output_dir / "analyses_completes.json"
    json_path.write_text(json.dumps(all_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return json_path