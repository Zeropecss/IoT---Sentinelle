#!/bin/bash

# Extraction de l'adresse MAC Bluetooth
MAC_ADDR=$(hciconfig hci0 | grep -oE "([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}")

# Génération des UUID de service et de caractéristique
SERVICE_UUID=$(uuidgen)
CHAR_UUID=$(uuidgen)

# Génération de la clé AES-128 (16 octets / 32 caractères hex)
AES_KEY=$(openssl rand -hex 16)

# Création du payload JSON
PAYLOAD=$(jq -n \
  --arg m "$MAC_ADDR" \
  --arg s "$SERVICE_UUID" \
  --arg c "$CHAR_UUID" \
  --arg k "$AES_KEY" \
  '{m: $m, s: $s, c: $c, k: $k}')

# Génération du QR Code sous forme d'image
echo "$PAYLOAD" | qrencode -o sentinel_qr.png

# Sauvegarde de la configuration pour le processus BLE
echo "$PAYLOAD" > config_ble.json

echo "QR Code généré pour l'adresse $MAC_ADDR"
