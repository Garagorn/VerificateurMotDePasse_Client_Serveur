import tkinter as tk
from tkinter import messagebox

class AuthGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Client d'Authentification")
        self.root.geometry("400x300")
        
        # Titre
        tk.Label(self.root, text="Système d'Authentification", 
                 font=("Arial", 16)).pack(pady=20)
        
        # Frame pour les champs
        frame = tk.Frame(self.root)
        frame.pack(pady=20)
        
        # Username
        tk.Label(frame, text="Nom d'utilisateur:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.username_entry = tk.Entry(frame, width=25)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        tk.Label(frame, text="Mot de passe:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.password_entry = tk.Entry(frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Boutons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="S'inscrire", 
                  command=self.on_register, width=12).pack(side='left', padx=10)
        tk.Button(button_frame, text="Se connecter", 
                  command=self.on_login, width=12).pack(side='left', padx=10)
        
    def on_register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Pour l'instant, juste afficher
        messagebox.showinfo("Register", f"Inscription: {username}")
        
    def on_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Pour l'instant, juste afficher
        messagebox.showinfo("Login", f"Connexion: {username}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AuthGUI()
    app.run()