#Reutilisation des fonctions
from Common.protocol import envoyer_message, recevoir_message
from Serveur.Verificateur.server_score import (
    score_structure, analyser_date_naissance,
    penalites_securite, est_valide, niveau
)
from Serveur.Verificateur.server_verif_dico import verification_dictionnaire

import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from queue import Queue
import socket
import ssl

SEUIL_VALIDE = 60   


"""
Calculer en local la force du mot de passe pour eviter d'evoyer au Serveur le mot de passe en clair
"""
def calculer_score(password: str, username: str,nom: str, prenom: str, naissance: str) -> tuple:
    if not password:
        return 0, []

    infos = [username, nom, prenom, naissance]

    score_struct, _ = score_structure(password)

    try:
        zx = verification_dictionnaire(password, infos)
        zx_score = zx["score"]
    except Exception:
        zx_score = 2  # valeur neutre

    date_fragments = analyser_date_naissance(password, naissance)
    penalty, issues = penalites_securite(
        password, nom, prenom, date_fragments, zx_score
    )

    total = max(0, score_struct + penalty)
    total = min(total, 40 if issues else 100)
    return total, issues


def niveau_couleur(score: int) -> tuple:
    """Retourne (label_niveau, couleur_hex) en reutilisant niveau() de server_score."""
    label = niveau(score)
    if score < 40: return label, "#e74c3c"
    if score < 60: return label, "#e67e22"
    if score < 75: return label, "#f0b429"
    if score < 90: return label, "#2ecc71"
    return label,             "#27ae60"


# Threads pour le reseau

class NetworkThread(Thread):
    """Thread dedie a la communication reseau"""

    def __init__(self, host: str, port: int,
                response_queue: Queue, command_queue: Queue,
                use_tls: bool = False):
        super().__init__()
        self.host           = host
        self.port           = port
        self.response_queue = response_queue
        self.command_queue  = command_queue
        self.use_tls        = use_tls #Specifier l'utilisation de TLS
        self.sock           = None
        self.running        = True
        self.daemon         = True

    #Mettre en place le contexte TLS pour le client
    def _make_tls_context(self) -> ssl.SSLContext:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode    = ssl.CERT_NONE
        return ctx

    def connect(self) -> bool:
        try:
            raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw_sock.settimeout(5)
            raw_sock.connect((self.host, self.port))
        #Utilisation du contexte pour la communication
            if self.use_tls:
                ctx       = self._make_tls_context()
                self.sock = ctx.wrap_socket(raw_sock, server_hostname=self.host)
            else:
                self.sock = raw_sock

            return True
        except Exception as e:
            #Ajouer la reponse dans la queue
            self.response_queue.put({
                "type": "error",
                "message": f"Connexion echouee : {e}"
            })
            return False

    """
    Envoyer les  donnees vers le serveur
    """
    def _send(self, data: dict):
        try:
                        #Socket et donnee
            envoyer_message(self.sock, data)
        except Exception as e:
            self.response_queue.put({"type": "error","message": f"Erreur d'envoi : {e}"})

    def run(self):
        while self.running:
            try:
                command = self.command_queue.get(timeout=1.0)
            except Exception:
                continue

        #Action suivant le type de commande
            if command["type"] == "stop":
                break

            if command["type"] == "send":
                self._send(command["data"])
                response = recevoir_message(self.sock)
            #Action suivant la reponse ou non du serveur
                if response:
                    self.response_queue.put({"type": "response", "data": response})
                else:
                    self.response_queue.put({"type": "error","message": "Connexion fermee par le serveur"})
                    break

        if self.sock:
            self.sock.close()


#  INTERFACE GRAPHIQUE

class ClientGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Authentification") #Titre
        self.root.resizable(False, False) #Ajuster la taille -> non

    #Queue pour les reponses et communications
        self.response_queue: Queue = Queue()
        self.command_queue:  Queue = Queue()

    #Son reseau de communication                                                              Utilisation de TLS
        self.network = NetworkThread("127.0.0.1", 65432, self.response_queue, self.command_queue, use_tls=True)

    #Probleme de connexion au serveur
        if not self.network.connect():
            messagebox.showerror("Erreur", "Impossible de se connecter au serveur")
            self.root.destroy()
            return

    #Actions au lancement
        self.network.start()

        #Test de connexion
        self.command_queue.put({
            "type": "send",
            "data": {"action": "hello"}
        })


        self._build_ui()
        self._check_responses()

        self.root.protocol("WM_DELETE_WINDOW", self._on_quit) #Detruire la fenetre a la fermeture

    """
    Construction de l'interface graphique
    """
    def _build_ui(self):
        self.root.configure(bg="#f0f2f5") #Couleur de bg

        # En-tête
        header = tk.Frame(self.root, bg="#2c3e50", pady=14)
        header.pack(fill="x")
        tk.Label(header, text="Système d'Authentification",font=("Segoe UI", 15, "bold"),bg="#2c3e50", fg="white").pack()

        # Onglets
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",     background="#f0f2f5", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"),padding=[18, 6], background="#dce1e7", foreground="#555")
        style.map("TNotebook.Tab",background=[("selected", "#2c3e50")],foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=12)

        tab_reg = tk.Frame(self.notebook, bg="#f0f2f5")
        tab_log = tk.Frame(self.notebook, bg="#f0f2f5")
        self.notebook.add(tab_reg, text="Inscription  ")
        self.notebook.add(tab_log, text="Connexion  ")

        #Construction du contenu des onglets
        self._build_tab_inscription(tab_reg)
        self._build_tab_connexion(tab_log)

        # Bouton Quitter
        quit_bar = tk.Frame(self.root, bg="#f0f2f5")
        quit_bar.pack(fill="x", padx=16, pady=(0, 14))
        tk.Button(quit_bar, text="Quitter",
                  command=self._on_quit,
                  bg="#e74c3c", fg="white",
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", cursor="hand2",
                  padx=12, pady=5).pack(side="right")

    # Inscription

    def _build_tab_inscription(self, parent: tk.Frame):
        pad = dict(padx=10, pady=5)
        form = tk.Frame(parent, bg="#f0f2f5")
        form.pack(padx=20, pady=16, fill="both")

        # (label affiche, cle interne, show)
        fields = [
            ("Nom d'utilisateur :", "username",  ""),
            ("Mot de passe :",      "password",  "*"),
            ("Confirmer :",         "confirm",   "*"),
            ("Nom :",               "nom",       ""),
            ("Prenom :",            "prenom",    ""),
            ("Date de naissance :", "naissance", ""),
        ]

        self._reg_entries: dict[str, tk.Entry] = {}
        for row, (label, key, show) in enumerate(fields):
            tk.Label(form, text=label, bg="#f0f2f5",font=("Segoe UI", 9), anchor="e", width=20
                     ).grid(row=row, column=0, sticky="e", **pad)
            entry = tk.Entry(form, width=28, show=show,font=("Segoe UI", 9), relief="solid", bd=1)
            entry.grid(row=row, column=1, sticky="w", **pad)
            self._reg_entries[key] = entry

        # Jauge de force
        gauge_frame = tk.Frame(parent, bg="#f0f2f5")
        gauge_frame.pack(fill="x", padx=30, pady=(0, 4))

        tk.Label(gauge_frame, text="Force du mot de passe :",bg="#f0f2f5", font=("Segoe UI", 8, "bold")).pack(anchor="w")

        self._strength_var = tk.IntVar(value=0)
        self._strength_bar = ttk.Progressbar(
            gauge_frame, variable=self._strength_var,
            maximum=100, length=320, mode="determinate"
        )
        self._strength_bar.pack(fill="x", pady=2)

        self._strength_label = tk.Label(
            gauge_frame, text="—", bg="#f0f2f5",
            font=("Segoe UI", 8, "italic"), fg="#888"
        )
        self._strength_label.pack(anchor="w")

        self._issues_label = tk.Label(
            gauge_frame, text="", bg="#f0f2f5",
            font=("Segoe UI", 8), fg="#e74c3c",
            wraplength=320, justify="left"
        )
        self._issues_label.pack(anchor="w")

    #Boutons pour l'onglet d'inscription
        btn_frame = tk.Frame(parent, bg="#f0f2f5")
        btn_frame.pack(pady=8)

        self._reg_submit_btn = tk.Button(
            btn_frame, text="S'inscrire",
            command=self._on_register,
            bg="#27ae60", fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2",
            padx=14, pady=6, state="disabled"
        )
        self._reg_submit_btn.pack(side="left", padx=8)

        tk.Button(btn_frame, text="Effacer",
                  command=self._clear_inscription,
                  bg="#7f8c8d", fg="white",
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", cursor="hand2",
                  padx=14, pady=6
                  ).pack(side="left", padx=8)

    # Mise a jour de la jauge a chaque frappe
        for key in ("password", "username", "nom", "prenom", "naissance"):
            self._reg_entries[key].bind("<KeyRelease>",lambda _e: self._update_strength())

    # Onglet Connexion

    def _build_tab_connexion(self, parent: tk.Frame):
        pad = dict(padx=10, pady=8)
        form = tk.Frame(parent, bg="#f0f2f5")
        form.pack(padx=20, pady=40, fill="both")

        tk.Label(form, text="Nom d'utilisateur :", bg="#f0f2f5",font=("Segoe UI", 9), width=18, anchor="e").grid(row=0, column=0, sticky="e", **pad)
        self._login_user = tk.Entry(form, width=28,font=("Segoe UI", 9), relief="solid", bd=1)
        self._login_user.grid(row=0, column=1, sticky="w", **pad)

        tk.Label(form, text="Mot de passe :", bg="#f0f2f5",font=("Segoe UI", 9), width=18, anchor="e"
                 ).grid(row=1, column=0, sticky="e", **pad)
        self._login_pwd = tk.Entry(form, width=28, show="*",font=("Segoe UI", 9), relief="solid", bd=1)
        self._login_pwd.grid(row=1, column=1, sticky="w", **pad)

        btn_frame = tk.Frame(parent, bg="#f0f2f5")
        btn_frame.pack(pady=8)

    #Boutons pour l'onglet de connexion
        tk.Button(btn_frame, text="Se connecter",
                  command=self._on_login,
                  bg="#2980b9", fg="white",
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", cursor="hand2",
                  padx=14, pady=6
                  ).pack(side="left", padx=8)

        tk.Button(btn_frame, text="Effacer",
                  command=self._clear_connexion,
                  bg="#7f8c8d", fg="white",
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", cursor="hand2",
                  padx=14, pady=6
                  ).pack(side="left", padx=8)

    # Jauge

    def _update_strength(self):
        e = self._reg_entries
        score, issues = calculer_score(
            e["password"].get(),
            e["username"].get(),
            e["nom"].get(),
            e["prenom"].get(),
            e["naissance"].get()
        )

        self._strength_var.set(score)
        label_txt, color = niveau_couleur(score)
        self._strength_label.config(text=f"{label_txt}  ({score}/100)", fg=color)

        style = ttk.Style()
        style.configure("green.Horizontal.TProgressbar",troughcolor="#dce1e7", background="#2ecc71")
        style.configure("yellow.Horizontal.TProgressbar",troughcolor="#dce1e7", background="#f0b429")
        style.configure("red.Horizontal.TProgressbar",troughcolor="#dce1e7", background="#e74c3c")

        if score >= 75:
            self._strength_bar.configure(style="green.Horizontal.TProgressbar")
        elif score >= SEUIL_VALIDE:
            self._strength_bar.configure(style="yellow.Horizontal.TProgressbar")
        else:
            self._strength_bar.configure(style="red.Horizontal.TProgressbar")

        self._issues_label.config(
            text=("Problèmes : " + " | ".join(issues)) if issues else ""
        )
        self._reg_submit_btn.config(
            state="normal" if score >= SEUIL_VALIDE else "disabled"
        )

# Actions

    """
    Enrigistrement d'une personne
    """
    def _on_register(self):
        e = self._reg_entries
        username  = e["username"].get().strip()
        password  = e["password"].get()
        confirm   = e["confirm"].get()
        nom       = e["nom"].get().strip()
        prenom    = e["prenom"].get().strip()
        naissance = e["naissance"].get().strip()

        if not all([username, password, confirm]):
            messagebox.showwarning("Champs manquants",
                                   "Nom d'utilisateur, mot de passe et confirmation sont obligatoires.")
            return

    #Confirmation du mdp different du mdp
        if password != confirm:
            messagebox.showerror("Erreur", "Les deux mots de passe ne correspondent pas.")
            return

        # Garde-fou final (au cas où le bouton serait contourne)
        score, issues = calculer_score(password, username, nom, prenom, naissance)
        if not est_valide(score):
            messagebox.showerror(
                "Mot de passe trop faible",
                f"Score : {score}/100" +
                (f"\nProblèmes : {', '.join(issues)}" if issues else "")
            )
            return
    #Envoie des donnees pour l'enregristrement
        self.command_queue.put({
            "type": "send",
            "data": {
                "action":    "register",
                "username":  username,
                "password":  password,
                "nom":       nom,
                "prenom":    prenom,
                "naissance": naissance
            }
        })

    """
    Login d'une personne
    """
    def _on_login(self):
        username = self._login_user.get().strip()
        password = self._login_pwd.get()

        if not username or not password:
            messagebox.showwarning("Champs manquants", "Remplissez tous les champs.")
            return

    #Envoie de la requete de connexion
        self.command_queue.put({
            "type": "send",
            "data": {
                "action":   "login",
                "username": username,
                "password": password
            }
        })

    def _clear_inscription(self):
        for entry in self._reg_entries.values():
            entry.delete(0, tk.END)
        self._strength_var.set(0)
        self._strength_label.config(text="—", fg="#888")
        self._issues_label.config(text="")
        self._reg_submit_btn.config(state="disabled")

    def _clear_connexion(self):
        self._login_user.delete(0, tk.END)
        self._login_pwd.delete(0, tk.END)

# Reponses
    def _check_responses(self):
        while not self.response_queue.empty():
            self._handle_response(self.response_queue.get())
        self.root.after(100, self._check_responses)

    def _handle_response(self, message: dict):
        msg_type = message.get("type")

        if msg_type == "response":
            data   = message["data"]
            status = data.get("status")
            msg    = data.get("message", "")
            score  = data.get("score")

            if status == "success":
                info = msg + (f"\n\nScore : {score}/100" if score is not None else "")
                messagebox.showinfo("Succès", info)
                active = self.notebook.index(self.notebook.select())
                if active == 0:
                    self._clear_inscription()
                else:
                    self._clear_connexion()
            else:
                messagebox.showerror("Erreur", msg)

        elif msg_type == "error":
            messagebox.showerror("Erreur reseau", message["message"])


    def _on_quit(self):
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter ?"):
            self.command_queue.put({"type": "stop"})
            self.network.join(timeout=2)
            self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = ClientGUI()
        app.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Appuie sur Entree pour quitter...")
