import socket
from Common.protocol import envoyer_message, recevoir_message

HOST = "127.0.0.1"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    # Envoyer un message structure
    message = {
        "action": "register",
        "username": "aliceToto",
        "password": "MonMotDePasse123!",
        "nom": "Toto",
        "prenom": "Alice",
        "naissance": "20/02/2002"
    }

    message = {
        "action": "login",
        "username": "aliceToto",
        "password": "MonMotDePasse123!",
    }
    envoyer_message(s, message)
    
    # Recevoir la reponse
    response = recevoir_message(s)
    print(f"Reçu : {response}")