STOPWORDS = {
    "de","des","du","la","le","les","et","ou","pour","avec","en","sur",
    "taille","t","the","un","une","bon","tres","très","etat","état"
}

HIGH_DEMAND = {
    "nike","zara","uniqlo","mango","sezane","sézane","adidas","levi's","levis",
    "ralph lauren","the north face","new balance","carhartt","vintage","gucci",
    "balenciaga","stone island","ami","jacquemus","isabel marant","acne studios",
    "diesel","tommy hilfiger","lacoste","fred perry","patagonia","columbia"
}

MID_DEMAND = {
    "hm","h&m","bershka","pull&bear","stradivarius","etam","kiabi","promod",
    "camaieu","jules","celio","jennyfer","la redoute","pimkie","naf naf"
}

STATE_BOOST = {
    "neuf": 1.0,
    "neuf avec étiquette": 1.3,
    "très bon état": 0.9,
    "bon état": 0.6,
    "satisfaisant": 0.2,
}

CATEGORY_MAP = {
    "robe":"robe","jean":"jean","pantalon":"pantalon","veste":"veste",
    "manteau":"manteau","pull":"pull","sweat":"sweat","chemise":"chemise",
    "top":"top","blouse":"blouse","jupe":"jupe","sac":"sac",
    "basket":"baskets","chauss":"chaussures","talon":"chaussures à talons",
    "botte":"bottes","short":"short","legging":"legging",
    "combinaison":"combinaison","blazer":"blazer","cardigan":"cardigan",
    "débardeur":"débardeur","parka":"parka","doudoune":"doudoune",
}