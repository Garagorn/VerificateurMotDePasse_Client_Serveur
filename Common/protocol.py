import json

def envoyer_message(sock, message_dict):
    """Envoie un dictionnaire Python en JSON"""
    message_json = json.dumps(message_dict)
    message_bytes = message_json.encode('utf-8')
    
    # Envoyer d'abord la taille (4 bytes)
    message_length = len(message_bytes)
    sock.sendall(message_length.to_bytes(4, byteorder='big'))
    
    # Puis le message
    sock.sendall(message_bytes)

def recevoir_message(sock):
    """Reçoit un message JSON et retourne un dictionnaire"""
    # Recevoir la taille (4 bytes)
    length_bytes = sock.recv(4)
    if not length_bytes:
        return None
    
    message_length = int.from_bytes(length_bytes, byteorder='big')
    
    # Recevoir le message complet
    message_bytes = b''
    while len(message_bytes) < message_length:
        chunk = sock.recv(message_length - len(message_bytes))
        if not chunk:
            return None
        message_bytes += chunk
    
    message_json = message_bytes.decode('utf-8')
    return json.loads(message_json)