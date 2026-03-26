import json
import dbus
import dbus.service
import dbus.mainloop.glib
import os
from bluezero import adapter, peripheral

# Identifiants D-Bus pour BlueZ
BUS_NAME = 'org.bluez'
AGENT_PATH = "/test/agent"
AGENT_INTERFACE = 'org.bluez.Agent1'

class SentinelAgent(dbus.service.Object):
    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def RequestConfirmation(self, device, passkey):
        """Appelée si le mode Just Works est activé par le téléphone"""
        print(f"Agent : Fallback Just Works activé pour {device}")
        return 

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        """Autorise la connexion GATT sans confirmation manuelle"""
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        print("Agent : Procédure de sécurité annulée")

def setup_bluetooth_hardware(config):
    """Configure les paramètres radio et la sécurité OOB"""
    # 1. Activation des capacités OOB au niveau du contrôleur
    # 'le on' active le BLE, 'connectable on' permet les liaisons
    os.system("sudo btmgmt power off")
    os.system("sudo btmgmt bredr off")
    os.system("sudo btmgmt le on")
    os.system("sudo btmgmt connectable on")
    os.system("sudo btmgmt pairable on")
    
    # 2. Réglage de l'intervalle d'annonce (4 secondes pour la batterie)
    os.system("sudo btmgmt advint 6400") # 6400 * 0.625ms = 4000ms
    
    os.system("sudo btmgmt power on")
    print(f"Matériel configuré avec la clé OOB : {config['k']}")

def run_sentinel():
    with open('config_sentinel.json', 'r') as f:
        config = json.load(f)

    # Initialisation de l'agent de sécurité
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    agent = SentinelAgent(bus, AGENT_PATH)
    
    obj = bus.get_object(BUS_NAME, "/org/bluez")
    manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
    manager.RequestDefaultAgent(AGENT_PATH)

    # Configuration matérielle
    setup_bluetooth_hardware(config)

    # Lancement du service GATT
    adpt = list(adapter.Adapter.available())[0]
    app = peripheral.Peripheral(adpt.address, local_name='Sentinel-STRI')
    app.add_service(srv_id=1, uuid=config['s'], primary=True)
    app.add_characteristic(srv_id=1, chr_id=1, uuid=config['c'],
                                value=[], notifying=False,
                                flags=['read', 'encrypt-read'],
                                read_callback=lambda: list(open("data_environnement.csv", "rb").read()))

    print("Sentinelle en attente de collecte...")
    app.publish()

if __name__ == '__main__':
    run_sentinel()
