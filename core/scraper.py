from __future__ import annotations
import sys
import time
from typing import List
from .models import ItemInput

try:
    from vinted_scraper import VintedScraper
except ImportError:
    VintedScraper = None


def scrape_user_items(username: str, country: str = "fr", max_items: int = 50, delay: float = 1.0) -> List[ItemInput]:
    """Scrape items from a Vinted user profile.
    
    Args:
        username: Vinted user username
        country: Country code (fr/be/es/de/it)
        max_items: Maximum number of items to scrape
        delay: Delay between requests in seconds
        
    Returns:
        List of ItemInput objects
    """
    if VintedScraper is None:
        print("[ERROR] vinted_scraper non installe. Lance : pip install vinted_scraper==2.4.0")
        sys.exit(1)

    scraper = VintedScraper(f"https://www.vinted.{country}")
    print(f"[INFO] Scraping Vinted - vendeur : {username}")

    params = {
        "search_text": username,
        "per_page": min(max_items, 96),
        "order": "newest_first",
    }

    try:
        raw_items = scraper.search(params)
    except Exception as exc:
        print(f"[WARN] Erreur scraping : {exc}")
        print("   Augmente --delay ou verifie ta connexion.")
        return []

    if not raw_items:
        print("   Aucun article trouve pour ce pseudo.")
        return []

    results: List[ItemInput] = []
    for it in raw_items[:max_items]:
        try:
            price = None
            raw_price = getattr(it, "price", None)
            if raw_price is not None:
                try: price = float(str(raw_price).replace(",", "."))
                except ValueError: pass

            photos = []
            for ph in (getattr(it, "photos", None) or []):
                u = getattr(ph, "full_size_url", None) or getattr(ph, "url", None)
                if u: photos.append(u)

            m = getattr(it, "brand_title", None) or getattr(it, "brand", None)
            s = getattr(it, "status", None)

            results.append(ItemInput(
                titre       = getattr(it, "title", "") or "",
                description = getattr(it, "description", "") or "",
                prix_actuel = price,
                marque      = str(m) if m else None,
                etat        = str(s) if s else None,
                vues        = getattr(it, "view_count", None),
                favoris     = getattr(it, "favourite_count", None),
                images      = photos,
                url         = getattr(it, "url", None),
            ))
        except Exception as e:
            print(f"  [WARN] Article ignore : {e}")
        time.sleep(delay)

    print(f"[OK] {len(results)} article(s) recupere(s).")
    return results