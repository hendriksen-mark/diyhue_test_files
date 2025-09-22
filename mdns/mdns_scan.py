from zeroconf import ServiceBrowser, Zeroconf
from flask import Flask, jsonify
import threading
import time
import os
import requests

app = Flask(__name__)
bridges = []
curdir = os.path.dirname(os.path.abspath(__file__))

class HueListener:
    def __init__(self):
        self.found_ids = set()

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info and b'bridgeid' in info.properties:
            bridgeid = info.properties[b'bridgeid'].decode()
            if bridgeid not in self.found_ids:
                self.found_ids.add(bridgeid)
                addresses = info.parsed_addresses()
                ip = addresses[0] if addresses else ""
                # Fetch bridge config
                macaddress = ""
                name = ""
                try:
                    resp = requests.get(f"http://{ip}/api/0/config", timeout=2)
                    if resp.ok:
                        data = resp.json()
                        macaddress = data.get("mac", "")
                        name = data.get("name", "")
                        port = info.port
                except Exception:
                    port = info.port
                bridges.append({
                    "id": bridgeid.lower(),
                    "internalipaddress": ip,
                    "macaddress": macaddress,
                    "name": name,
                    "port": port
                })

    def remove_service(self, zeroconf, type, name):
        pass  # Not needed for scanning

    def update_service(self, zeroconf, type, name):
        pass  # Not needed, but required by zeroconf

def mdns_scan():
    zeroconf = Zeroconf()
    listener = HueListener()
    browser = ServiceBrowser(zeroconf, "_hue._tcp.local.", listener)
    try:
        while True:
            time.sleep(1)
    finally:
        zeroconf.close()

@app.route("/")
def list_bridges():
    return jsonify(bridges)

def run_https():
    app.run(host="0.0.0.0", port=443, ssl_context=(os.path.join(curdir, "fullchain.pem"), os.path.join(curdir, "key.pem")))

def run_http():
    app.run(host="0.0.0.0", port=80)

if __name__ == "__main__":
    threading.Thread(target=mdns_scan, daemon=True).start()
    threading.Thread(target=run_https, daemon=True).start()
    run_http()
