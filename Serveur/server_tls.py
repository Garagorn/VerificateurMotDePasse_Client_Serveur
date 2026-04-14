import socket
import ssl
import os
from threading import Thread

from Common.protocol import envoyer_message, recevoir_message
from Serveur.auth import handle_register, handle_login
from Serveur.config_logger import setup_logger
from Serveur.server import handle_client 

HOST = "127.0.0.1"
PORT = 65432

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
cert_path = os.path.join(BASE_DIR, "certs/server.crt")
key_path  = os.path.join(BASE_DIR, "certs/server.key")

logger = setup_logger()

"""
Mettre en place le contexte pour TLS
"""
def make_tls_context() -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    #Charger les cles
    ctx.load_cert_chain(certfile=cert_path, keyfile=key_path)
    return ctx

"""
Serveur reutilise mais adapter a TLS
"""
def main():
    tls_ctx = make_tls_context()


    logger.info("Demarrage du serveur TLS", extra={
        "event": "server_tls_start", "host": HOST, "port": PORT
    })

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as raw_server:
        raw_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        raw_server.bind((HOST, PORT))
        raw_server.listen(5)

        logger.info("Serveur TLS en ecoute", extra={
            "event": "server_tls_listening", "host": HOST, "port": PORT
        })

        while True:
            raw_conn, addr = raw_server.accept()
            try:
                tls_conn = tls_ctx.wrap_socket(raw_conn, server_side=True)
            except ssl.SSLError as e:
                logger.warning(f"Handshake TLS echoue depuis {addr}: {e}")
                raw_conn.close()
                continue

            # handle_client recoit une tls_conn — transparent pour lui
            t = Thread(target=handle_client, args=(tls_conn, addr), daemon=True)
            t.start()


if __name__ == "__main__":
    main()