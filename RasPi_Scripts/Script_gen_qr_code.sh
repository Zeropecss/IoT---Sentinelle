#!/bin/bash

# Définition des fichiers de sortie
CONFIG_FILE="config_sentinel.json"
QR_IMAGE="sentinel_qr.png"

# Extraction de l'adresse MAC de l'adaptateur Bluetooth hci0
MAC_ADDR="E4:5F:01:DE:E6:B6"

# Génération des UUID pour le Service et la Caractéristique GATT
SERVICE_UUID=$(uuidgen)
CHAR_UUID=$(uuidgen)

# Génération d'une clé AES-128 (16 octets / 32 caractères hexadécimaux)
AES_KEY=$(openssl rand -hex 16)

# Construction du payload JSON compact
# m: MAC, s: Service UUID, c: Char UUID, k: AES Key
PAYLOAD=$(jq -n \
  --arg m "$MAC_ADDR" \
  --arg s "$SERVICE_UUID" \
  --arg c "$CHAR_UUID" \
  --arg k "$AES_KEY" \
  '{m: $m, s: $s, c: $c, k: $k}')

# Sauvegarde de la configuration technique
echo "$PAYLOAD" > "$CONFIG_FILE"

# Génération du QR Code statique
echo "$PAYLOAD" | qrencode -s 6 -o "$QR_IMAGE"

echo "Provisionnement terminé."
echo "Adresse MAC : $MAC_ADDR"
echo "Service UUID : $SERVICE_UUID"
echo "Configuration sauvegardée dans $CONFIG_FILE"
