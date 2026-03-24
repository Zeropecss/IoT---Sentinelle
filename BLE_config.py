from bluezero import adapter, peripheral
import json

# Chargement de la configuration générée à l'étape 1
with open("config_ble.json", "r") as f:
    config = json.load(f)

def on_read_data():
    # Logique de lecture du fichier CSV avec segmentation
    try:
        with open("data_environnement.csv", "rb") as f:
            return list(f.read()) # À segmenter selon le MTU réel
    except FileNotFoundError:
        return list(b"Erreur: Fichier absent")

def start_ble_peripheral():
    # Initialisation de l'adaptateur
    adpt = list(adapter.Adapter.available())[0]
    sentinel = peripheral.Peripheral(adpt.address, local_name='Sentinelle-STRI')

    # Ajout du service et de la caractéristique de transfert
    # L'accès est protégé par les mécanismes de sécurité définis au QR code
    sentinel.add_service(srv_id=1, uuid=config['s'], primary=True)
    sentinel.add_characteristic(srv_id=1, chr_id=1, uuid=config['c'],
                                value=[], notifying=False,
                                flags=['read', 'encrypt-read'],
                                read_callback=on_read_data)

    # Lancement de l'advertisement permanent [cite: 10]
    print(f"Sentinelle en attente de connexion sur {config['m']}...")
    sentinel.publish()

if __name__ == '__main__':
    start_ble_peripheral()
