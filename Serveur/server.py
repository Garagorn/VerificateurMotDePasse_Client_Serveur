import socket
from Common.protocol import envoyer_message, recevoir_message
from Serveur.auth import handle_register, handle_login
from Serveur.config_logger import setup_logger

HOST = "127.0.0.1"
PORT = 65432

#Init logger
logger = setup_logger()

"""
Gere un client connecte
"""
def handle_client(conn, addr):

    logger.info("Nouvelle connexion", extra={
        "event": "client_connected",
        "client_ip": addr[0],
        "client_port": addr[1]
    })

    
    try:
        while True:
            message = recevoir_message(conn)
            if not message:
                logger.warning(f"Connexion fermee par {addr}")
                break
            
            action = message.get("action")
            username = message.get("username", "unknown")
            
            logger.info("Action reçue", extra={
                "event": "action_received",
                "action": action,
                "username": username,
                "client_ip": addr[0]
            })

            if action == "register":
                reponse = handle_register(message["username"], message["password"])
                
                logger.info("Tentative d'enregistrement", extra={
                    "event": "register_attempt",
                    "username": username,
                    "success": reponse["status"] == "success",
                    "client_ip": addr[0]
                })
            
            elif action == "login":
                reponse = handle_login(message["username"], message["password"])
                
                logger.info("Tentative de connexion", extra={
                    "event": "login_attempt",
                    "username": username,
                    "success": reponse["status"] == "success",
                    "client_ip": addr[0]
                })
            
            else:
                reponse = {"status": "error", "message": "Action inconnue"}
            
                logger.warning("Action inconnue", extra={
                    "event": "unknown_action",
                    "action": action,
                    "client_ip": addr[0]
                })

            envoyer_message(conn, reponse)
    
    except Exception as e:
        logger.error("Erreur de communication", extra={
            "event": "connection_error",
            "error": str(e),
            "client_ip": addr[0]
        }, exc_info=True)
    finally:
        conn.close()
        logger.info("Client deconnecte", extra={
            "event": "client_disconnected",
            "client_ip": addr[0]
        })


def main():
    logger.info("Demarrage du serveur", extra={
        "event": "server_start",
        "host": HOST,
        "port": PORT
    })

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        logger.info("Serveur en ecoute", extra={
            "event": "server_listening",
            "host": HOST,
            "port": PORT
        })

        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)

if __name__ == "__main__":
    main()