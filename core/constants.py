STOPWORDS = {
    "de", "des", "du", "la", "le", "les", "et", "ou", "pour", "avec", "en", "sur",
    "taille", "t", "the", "un", "une", "bon", "tres", "très", "etat", "état",
    "neuf", "neuve", "vendu", "offert", "gratuit", "livraison", "rapide",
}

HIGH_DEMAND = {
    # Sportswear / streetwear
    "nike", "adidas", "jordan", "new balance", "asics", "puma", "reebok",
    "converse", "vans", "carhartt", "champion", "stussy", "supreme",
    "the north face", "patagonia", "columbia", "arcteryx",
    # Mode française / premium
    "zara", "mango", "sezane", "sézane", "isabel marant", "jacquemus",
    "ami", "acne studios", "a.p.c.", "apc", "rouje", "ba&sh", "bash",
    "marant", "sandro", "maje", "claudie pierlot",
    # Denim / classics
    "levi's", "levis", "wrangler", "lee", "diesel",
    # Luxe
    "gucci", "balenciaga", "louis vuitton", "chanel", "dior",
    "saint laurent", "celine", "loewe", "bottega veneta",
    "stone island", "moncler", "canada goose",
    # Casual premium
    "ralph lauren", "tommy hilfiger", "lacoste", "fred perry",
    "uniqlo", "cos", "arket",
    # Vintage / tendance
    "vintage", "y2k", "archive",
}

MID_DEMAND = {
    "hm", "h&m", "bershka", "pull&bear", "stradivarius",
    "etam", "kiabi", "promod", "camaieu", "jules", "celio",
    "jennyfer", "la redoute", "pimkie", "naf naf", "gémo", "gemo",
    "primark", "shein", "bonobo", "devred", "maisons du monde",
}

STATE_BOOST = {
    "neuf avec étiquette": 1.5,
    "neuf":                1.1,
    "très bon état":       0.9,
    "bon état":            0.5,
    "satisfaisant":        0.1,
}

# Multiplicateur de prix selon état (pour pricing_strategy)
STATE_PRICE_MULT = {
    "neuf avec étiquette": 1.15,
    "neuf":                1.08,
    "très bon état":       1.00,
    "bon état":            0.88,
    "satisfaisant":        0.70,
}

CATEGORY_MAP = {
    "robe":          "robe",
    "jean":          "jean",
    "pantalon":      "pantalon",
    "veste":         "veste",
    "manteau":       "manteau",
    "pull":          "pull",
    "sweat":         "sweat",
    "chemise":       "chemise",
    "top":           "top",
    "blouse":        "blouse",
    "jupe":          "jupe",
    "sac":           "sac",
    "basket":        "baskets",
    "chauss":        "chaussures",
    "talon":         "chaussures à talons",
    "botte":         "bottes",
    "short":         "short",
    "legging":       "legging",
    "combinaison":   "combinaison",
    "blazer":        "blazer",
    "cardigan":      "cardigan",
    "débardeur":     "débardeur",
    "parka":         "parka",
    "doudoune":      "doudoune",
    "t-shirt":       "t-shirt",
    "tshirt":        "t-shirt",
    "gilet":         "gilet",
    "body":          "body",
    "maillot":       "maillot de bain",
    "bijou":         "bijoux",
    "accessoire":    "accessoire",
    "ceinture":      "ceinture",
    "écharpe":       "écharpe",
    "chapeau":       "chapeau",
    "casquette":     "casquette",
}
