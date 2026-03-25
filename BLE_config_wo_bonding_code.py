import json
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
from bluezero import adapter, peripheral

# Configuration de l'agent de sécurité BlueZ
BUS_NAME = 'org.bluez'
AGENT_PATH = "/test/agent"
AGENT_INTERFACE = 'org.bluez.Agent1'

class JustWorksAgent(dbus.service.Object):
    """
    Agent de sécurité configuré pour accepter toutes les requêtes
    sans intervention humaine.
    """
    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def DisplayConfirmation(self, device, passkey):
        print(f"Agent : Confirmation automatique pour {device} (Passkey: {passkey})")
        return # Retourne immédiatement pour valider

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print(f"Agent : Autorisation automatique pour {device}")
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        print("Agent : Appairage annulé par le client")

def setup_agent():
    """Initialise et enregistre l'agent avec la capacité NoInputNoOutput"""
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    agent = JustWorksAgent(bus, AGENT_PATH)
    
    obj = bus.get_object(BUS_NAME, "/org/bluez")
    manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    
    # 'NoInputNoOutput' est la clé pour éviter l'affichage de codes numériques
    manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
    manager.RequestDefaultAgent(AGENT_PATH)
    print("Agent enregistré en mode 'NoInputNoOutput' (Just Works)")

def run_sentinel():
    with open('config_sentinel.json', 'r') as f:
        config = json.load(f)

    # 1. Activation de l'agent Just Works
    setup_agent()

    # 2. Initialisation du serveur GATT (sans chiffrement pour ce test)
    adpt = list(adapter.Adapter.available())[0]
    app = peripheral.Peripheral(adpt.address, local_name='Sentinel-TEST')
    
    app.add_service(srv_id=1, uuid=config['s'], primary=True)
    app.add_characteristic(srv_id=1, chr_id=1, uuid=config['c'],
                                value=[], notifying=False,
                                flags=['read'], # Pas de 'encrypt-read' ici
                                read_callback=lambda: list(open("data_environnement.csv", "rb").read()))

    print(f"Sentinelle en attente sur {config['m']}...")
    app.publish()

if __name__ == '__main__':
    run_sentinel()
