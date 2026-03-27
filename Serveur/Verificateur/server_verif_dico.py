from zxcvbn import zxcvbn

def verification_dictionnaire(password, infos):

    pwd = password[:100]
    # Filtrer infos pour ne garder que les chaînes non vides
    infos_clean = [i for i in infos if isinstance(i, str) and i.strip()]
    try:
        return zxcvbn(pwd, user_inputs=infos_clean)
    except Exception as e:
        return {
            "score": 0,
            "feedback": {"suggestions": ["Erreur dans l'analyse dictionnaire"]},
            "crack_times_display": {"offline_slow_hashing_1e4_per_second": "Inconnu"}
        }

def score_zxcvbn(result):
    return result["score"]