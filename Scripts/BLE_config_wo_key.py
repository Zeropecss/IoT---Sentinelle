import json
from bluezero import adapter, peripheral

# Load the configuration (MAC, Service UUID, Char UUID)
with open('config_sentinel.json', 'r') as f:
    config = json.load(f)

class SentinelDiagnostic:
    def __init__(self, cfg):
        self.cfg = cfg
        self.file_path = "data_environnement.csv"
        
        # 1. Initialize Adapter
        adpts = list(adapter.Adapter.available())
        if not adpts:
            raise Exception("No Bluetooth adapter found.")
        
        self.app = peripheral.Peripheral(adpts[0].address, 
                                        local_name='Sentinel-TEST')
        
        # 2. Setup Service
        self.app.add_service(srv_id=1, uuid=self.cfg['s'], primary=True)
        
        # 3. Setup Characteristic (REMOVED 'encrypt-read')
        self.app.add_characteristic(srv_id=1, chr_id=1, uuid=self.cfg['c'],
                                    value=[], 
                                    notifying=False,
                                    flags=['read'],  # Open access for testing
                                    read_callback=self.read_csv_data)

    def read_csv_data(self):
        """Reads the CSV file and returns it as a byte list"""
        try:
            with open(self.file_path, 'rb') as f:
                print("Diagnostic: Data read request received!")
                return list(f.read())
        except Exception as e:
            print(f"Diagnostic Error: {e}")
            return list(b"FILE_ERROR")

    def run(self):
        print(f"DEBUG MODE: Sentinel advertising on {self.cfg['m']}")
        print(f"Connect with nRF Connect to Service: {self.cfg['s']}")
        self.app.publish()

if __name__ == '__main__':
    sentinel = SentinelDiagnostic(config)
    sentinel.run()
