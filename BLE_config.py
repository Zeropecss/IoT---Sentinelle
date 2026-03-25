import json
from bluezero import adapter, peripheral

# Chargement de la configuration statique générée par le script Bash
with open('config_sentinel.json', 'r') as f:
    config = json.load(f)

class SentinelPeripheral:
    def __init__(self, cfg):
        self.cfg = cfg
        self.file_path = "data_environnement.csv"
        
        # Initialisation de l'adaptateur Bluetooth
        adpt = list(adapter.Adapter.available())[0]
        self.app = peripheral.Peripheral(adpt.address, 
                                        local_name='Sentinel-STRI')
        
        # Définition du service et de la caractéristique de lecture
        self.app.add_service(srv_id=1, uuid=self.cfg['s'], primary=True)
        self.app.add_characteristic(srv_id=1, chr_id=1, uuid=self.cfg['c'],
                                    value=[], notifying=False,
                                    flags=['read', 'encrypt-read'],
                                    read_callback=self.read_csv_data)

    def read_csv_data(self):
        """
        Callback déclenché lors d'une lecture GATT.
        Retourne le contenu du fichier CSV. 
        Note : Une logique de segmentation (chunks) peut être ajoutée ici
        si le client ne supporte pas le MTU élevé.
        """
        try:
            with open(self.file_path, 'rb') as f:
                content = f.read()
                return list(content)
        except FileNotFoundError:
            return list(b"ERROR:FILE_NOT_FOUND")

    def run(self):
        print(f"Démarrage de l'annonce sur {self.cfg['m']}...")
        self.app.publish()

if __name__ == '__main__':
    sentinel = SentinelPeripheral(config)
    sentinel.run()
