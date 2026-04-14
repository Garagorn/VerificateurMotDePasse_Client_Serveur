import sqlite3 as sql
from Serveur.Verificateur.server_hashing import verifier,hasher
from Serveur.Verificateur.server_score import est_valide

import os

#Chemin absolu pour acceder a la bdd
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database.db"))

"""
Ajout de mot de passe a la bdd
"""
def ajouterMDP(username, mdp,score_total):
    if not username or not mdp:
        return False, "Champs vides"

    if not est_valide(score_total):
        return False, "Mot de passe trop faible"
    try:
        #Connection a la bdd
        conn = sql.connect(DB_PATH)
        cursor = conn.cursor()

        # Hashage
        hashed_password = hasher(mdp)

        # Insertion dans la bdd
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        #Fermeture de la connection
        conn.commit()
        conn.close()

#Résultats possibles pour l'ajout :
        return True, "Utilisateur ajouté"

    except sql.IntegrityError:
        return False, "Nom d'utilisateur déja existant"


"""
Vérification du mot de passe dans la bdd
"""
def verifierMDP(username, mdp):
    if not username or not mdp:
        return False, "Champs vides"

    #Connection a la bdd
    try:
        conn = sql.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username = ?",
            (username,)
        )

        result = cursor.fetchone()
        conn.close()

    #Résultats possibles :
        if result is None: #Pas d'user avec cet username
            return False, "Utilisateur introuvable"

        mdpBD = result[0] #mdp hashé depuis la base

        if verifier(mdp, mdpBD): #Il existe un user avec le bon mdp
            return True, "Mot de passe correspondant"
        else:   #Mdp différent pour cet user
            return False, "Mot de passe incorrect"

    except Exception as e:
        return False, f"Erreur : {e}"

"""
Vérifier la présence d'un utilisateur dans la bdd
"""
def verifier_Utilisateur(username):
    if not username:
        return False, "Champ vide"

    try:
        conn = sql.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM users WHERE username = ?",
            (username,)
        )

        result = cursor.fetchone()

        conn.commit()
        conn.close()

        if result:
            return True, "Utilisateur existant"
        else:
            return False, "Utilisateur introuvable"

    except Exception as e:
        return False, f"Erreur : {e}"

# if __name__ == "__main__":

#     with sql.connect(DB_PATH) as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT username FROM users")
#         print("Contenu table:", cursor.fetchall())

