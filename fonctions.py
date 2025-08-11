def argent_doublon(categorie: str, rarete: str) -> int:
    
    rarete_niveaux = {
        "Rare": 1,
        "Épique": 2,
        "Légendaire": 3,
        "Mythique": 4,
        "Divin": 5,
        "Prismatique": 6
    }

    categorie_facteurs = {
        "Décor": 1.0,
        "Kink": 1.3,
        "Mutation": 1.6,
        "Personnage": 2.0
    }

    R = rarete_niveaux.get(rarete, 1)
    C = categorie_facteurs.get(categorie, 1.0)

    base = 100
    max_base = 10000
    argent = base + (max_base - base) * ((R - 1) / 5) * C

    return int(argent)
