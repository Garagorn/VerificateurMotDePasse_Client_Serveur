import re

#Taille du mot de passe
def score_taille(password):
    n = len(password)

    if n < 8:
        return 0
    elif n < 12:
        return 15
    elif n < 16:
        return 25
    elif n < 20:
        return 35
    else:
        return 40

def score_categorie(password, pattern, min_count, max_score=15):
    n = len(re.findall(pattern, password))

    if n == 0:
        return 0, n
    elif n < min_count:
        return max_score // 2, n
    else:
        return max_score, n

def score_structure(password):
    score = score_taille(password)
    stats = {}

    rules = {
        "Majuscules": (r"[A-Z]", 2),
        "Minuscules": (r"[a-z]", 2),
        "Chiffres":   (r"\d",    2),
        "Spéciaux":   (r"[!@#$%^&*(),.?\":{}|<>]", 1),
    }

    for nom, (pattern, min_count) in rules.items():
        s, n = score_categorie(password, pattern, min_count)
        score += s
        stats[nom] = n

    return min(score, 100), stats


#Analyser la présence de la date de naissancce dans le mot de passe
def analyser_date_naissance(password, date):
    chiffres = re.findall(r"\d+", date)
    joined = "".join(chiffres)

    fragments = set(chiffres)

    if len(joined) >= 6:
        fragments.add(joined)
        fragments.add(joined[:4])
        fragments.add(joined[-4:])

    return [f for f in fragments if f and f in password]


def date_dans_mdp(password, date):
    fragments = analyser_date_naissance(password, date)
    return bool(fragments), fragments


def penalite_date(fragments):
    return -10 if fragments else 0


def niveau(score):
    if score < 40:
        return "Très faible"
    elif score < 60:
        return "Faible"
    elif score < 75:
        return "Correct"
    elif score < 90:
        return "Fort"
    else:
        return "Très fort"


def est_valide(score, seuil=60):
    return score >= seuil

#Penaliser la presencce de la date de naissance, du nom, du prenom ou un mot de passe trop simple
def penalites_securite(password, nom, prenom, date_fragments, zx_score):
    penalty = 0
    issues = []

    pwd = password.lower()

    if nom and nom.lower() in pwd:
        penalty -= 30
        issues.append("nom")

    if prenom and prenom.lower() in pwd:
        penalty -= 30
        issues.append("prenom")

    if date_fragments:
        if len(date_fragments) >= 2:
            penalty -= 40
            issues.append("date_complete")
        else:
            penalty -= 25
            issues.append("date_partielle")

    if zx_score == 0:
        penalty -= 50
        issues.append("dictionnaire_critique")
    elif zx_score == 1:
        penalty -= 35
        issues.append("dictionnaire_faible")

    return penalty, issues
