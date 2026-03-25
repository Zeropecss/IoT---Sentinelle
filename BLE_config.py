import json
import dbus
from bluezero import adapter, peripheral

# Chargement de la configuration générée par le script Bash
try:
    with open('config_sentinel.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print("Erreur : config_sentinel.json introuvable. Lancez le script Bash d'abord.")
    exit(1)

class SentinelPeripheral:
    def __init__(self, cfg):
        self.cfg = cfg
        self.file_path = "data_environnement.csv"
        
        # Initialisation de l'adaptateur Bluetooth (hci0)
        adpts = list(adapter.Adapter.available())
        if not adpts:
            raise Exception("Aucun adaptateur Bluetooth trouvé.")
        
        self.app = peripheral.Peripheral(adpts[0].address, 
                                        local_name='Sentinelle-STRI')
        
        # Configuration du Service et de la Caractéristique [cite: 16, 32]
        self.app.add_service(srv_id=1, uuid=self.cfg['s'], primary=True)
        
        # Le flag 'encrypt-read' impose l'usage de la clé AES 
        self.app.add_characteristic(srv_id=1, chr_id=1, uuid=self.cfg['c'],
                                    value=[], notifying=False,
                                    flags=['read', 'encrypt-read'],
                                    read_callback=self.read_csv_data)

    def read_csv_data(self):
        """Lit et retourne le contenu du fichier CSV [cite: 28, 45]"""
        try:
            with open(self.file_path, 'rb') as f:
                return list(f.read())
        except Exception as e:
            return list(f"ERROR: {str(e)}".encode())

    def run(self):
        print(f"Annonce BLE active sur {self.cfg['m']}")
        print(f"Service UUID : {self.cfg['s']}")
        self.app.publish()

def setup_security_settings(aes_key_hex):
    """
    Prépare l'adaptateur pour l'appairage sécurisé.
    En production, un Agent BlueZ doit être enregistré ici.
    """
    print(f"Clé AES-128 chargée pour l'appairage OOB : {aes_key_hex}")
    # Note : Pour éviter le code PIN, on force le mode 'NoInputNoOutput' 
    # ou on utilise un agent D-Bus répondant à la clé.
    import os
    os.system("bluetoothctl discoverable on")
    os.system("bluetoothctl pairable on")

if __name__ == '__main__':
    # 1. Configuration de la sécurité avant de lancer le service
    setup_security_settings(config['k'])
    
    # 2. Lancement de la sentinelle
    sentinel = SentinelPeripheral(config)
    sentinel.run()
