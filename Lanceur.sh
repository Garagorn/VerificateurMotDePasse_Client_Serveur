#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=== Demarrage du système Client-Serveur ===${NC}"
source venv/bin/activate

echo -e "\n${BLUE}[0/2] Nettoyage du port 65432...${NC}"
fuser -k 65432/tcp 2>/dev/null && sleep 0.5

echo -e "\n${BLUE}[1/2] Demarrage du serveur...${NC}"
python3 -m Serveur.server_tls &
SERVER_PID=$!

for i in $(seq 1 10); do
    echo | openssl s_client \
        -connect 127.0.0.1:65432 \
        -verify_quiet \
        -no_ign_eof 2>/dev/null \
        | grep -q "CONNECTED" && break
    sleep 0.5
done

echo -e "${BLUE}[2/2] Démarrage du client...${NC}"
python3 -m Client.interface_client

echo -e "${GREEN}Arret du serveur...${NC}"
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null
echo -e "${GREEN}=== Systeme arrêté ===${NC}"
