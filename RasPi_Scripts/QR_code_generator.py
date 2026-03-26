import qrcode
import json
import secrets
import uuid
from subprocess import check_output

def get_mac_address():
    # Récupère l'adresse MAC de l'interface Bluetooth par défaut
    try:
        output = check_output(["hciconfig", "hci0", "address"]).decode("utf-8")
        return output.split("Address: ")[1].split(" ")[0].strip()
    except Exception:
        return "AA:BB:CC:DD:EE:FF" # Valeur de secours pour test

# 1. Génération des identifiants et de la clé AES-128
mac_addr = get_mac_address()
service_uuid = str(uuid.uuid4())
char_uuid = str(uuid.uuid4())
aes_key = secrets.token_hex(16) # 16 octets = 128 bits

# 2. Structuration de la charge utile (Payload)
payload = {
    "MAC": mac_addr,          # Adresse MAC
    "SERV_ID": service_uuid,  # Service ID
    "CHAR_ID": char_uuid,     # Characteristic ID
    "KEY": aes_key            # Clé AES-128
}

# 3. Génération du QR Code
qr_json = json.dumps(payload)
img = qrcode.make(qr_json)
img.save("sentinel_qr.png")

# Sauvegarde des paramètres pour le service BLE
with open("config_ble.json", "w") as f:
    json.dump(payload, f)

print(f"QR Code généré avec succès pour la MAC {mac_addr}")
