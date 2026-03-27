from Serveur.Verificateur.server_score import score_structure, analyser_date_naissance, penalites_securite, est_valide
from Serveur.Verificateur.server_verif_dico import verification_dictionnaire
from Serveur.Verificateur.server_database import ajouterMDP, verifierMDP, verifier_Utilisateur

def handle_register(username, password, nom="", prenom="", naissance=""):
    """Gère l'enregistrement d'un utilisateur"""

    # Nettoyage
    username = username.strip()

    #Verifier si l'utilisateur existe
    exists, _ = verifier_Utilisateur(username)
    if exists:
        return {
            "status": "error",
            "message": "Nom d'utilisateur déjà existant"
        }

    #Analyse du mot de passe
    infos = [nom, prenom, naissance]

    score_struct, stats = score_structure(password)

    try:
        zx = verification_dictionnaire(password, infos)
        zx_score = zx["score"]
    except Exception:
        zx_score = 0
    date_fragments = analyser_date_naissance(password, naissance)
    penalty, issues = penalites_securite(
        password, nom, prenom, date_fragments, zx_score
    )

    score_total = max(0, score_struct + penalty)
    if issues:
        score_total = min(score_total, 40)
    else:
        score_total = min(score_total, 100)

    #Verification
    if not est_valide(score_total):
        return {
            "status": "error",
            "message": "Mot de passe trop faible",
            "score": score_total
        }

    success, message = ajouterMDP(username, password, score_total)

    if not success:
        return {
            "status": "error",
            "message": message
        }
    return {
        "status": "success",
        "message": "Compte créé",
        "score": score_total
    }



def handle_login(username, password):
    """Gère la connexion utilisateur"""

    username = username.strip()

    success, message = verifierMDP(username, password)
    if success:
        return {
            "status": "success",
            "message": "Connexion réussie"
        }
    else:
        return {
            "status": "error",
            "message": message
        }