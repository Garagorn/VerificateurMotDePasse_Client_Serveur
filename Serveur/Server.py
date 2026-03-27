import socket
from Common.protocol import envoyer_message, recevoir_message
from Serveur.auth import handle_register, handle_login

HOST = "127.0.0.1"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Serveur en écoute sur {HOST}:{PORT}")
    
    conn, addr = s.accept()
    with conn:
        print(f"Connecté par {addr}")
        
        while True:
            message = recevoir_message(conn)
            if not message:
                break
            
            action = message.get("action")
            
            if action == "register":
                response = handle_register(
                    message["username"],
                    message["password"],
                    message["nom"],
                    message["prenom"],
                    message["naissance"]
                )
            elif action == "login":
                response = handle_login(
                    message["username"],
                    message["password"]
                )
            else:
                response = {"status": "error", "message": "Action inconnue"}
            
            envoyer_message(conn, response)