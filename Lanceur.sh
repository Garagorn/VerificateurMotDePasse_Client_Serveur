#!/bin/bash

# Couleurs pour la lisibilité
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Démarrage du système Client-Serveur ===${NC}"

source venv/bin/activate

# Démarrer le serveur en arrière-plan
echo -e "${BLUE}[1/2] Démarrage du serveur...${NC}"
python3 -m Serveur.server &
SERVER_PID=$!

# Attendre que le serveur soit prêt
sleep 2

# Démarrer le client
echo -e "${BLUE}[2/2] Démarrage du client...${NC}"
python3 -m Client.interface_client

# Quand le client se ferme, arrêter le serveur
echo -e "${GREEN}Arrêt du serveur...${NC}"
kill $SERVER_PID

echo -e "${GREEN}=== Système arrêté ===${NC}"
