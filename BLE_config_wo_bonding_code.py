import json
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
from bluezero import adapter, peripheral

BUS_NAME = 'org.bluez'
AGENT_PATH = "/test/agent"
AGENT_INTERFACE = 'org.bluez.Agent1'

class JustWorksAgent(dbus.service.Object):
    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def RequestConfirmation(self, device, passkey):
        """
        Méthode CRITIQUE : Cette fonction est appelée lors de la comparaison numérique.
        Retourner sans erreur valide automatiquement le code affiché sur le smartphone.
        """
        print(f"Appairage automatique : Validation du code {passkey} pour {device}")
        return 

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print(f"Autorisation automatique pour {device}")
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        print("Requête d'appairage annulée")

def setup_agent():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    agent = JustWorksAgent(bus, AGENT_PATH)
    
    obj = bus.get_object(BUS_NAME, "/org/bluez")
    manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    
    # Enregistrement avec 'NoInputNoOutput' pour forcer le mode automatique
    manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
    manager.RequestDefaultAgent(AGENT_PATH)
    print("Agent de sécurité configuré en mode 'Just Works'.")

def run_sentinel():
    try:
        with open('config_sentinel.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Erreur : Fichier de configuration absent.")
        return

    setup_agent()

    adpt = list(adapter.Adapter.available())[0]
    app = peripheral.Peripheral(adpt.address, local_name='Sentinel-TEST')
    
    app.add_service(srv_id=1, uuid=config['s'], primary=True)
    app.add_characteristic(srv_id=1, chr_id=1, uuid=config['c'],
                                value=[], notifying=False,
                                flags=['read'], 
                                read_callback=lambda: list(open("data_environnement.csv", "rb").read()))

    print(f"Sentinelle prête sur {config['m']}. Lancez la connexion depuis le smartphone.")
    app.publish()

if __name__ == '__main__':
    run_sentinel()
