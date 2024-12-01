import WledDevice
import logManager
from light_types import lightTypes
import Light
import os
import yaml
import socket
import json

logging = logManager.logger.get_logger(__name__)

lightObject = {}

#configHandler.py

class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

def _open_yaml(path):
    with open(path, 'r', encoding="utf-8") as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)

def _write_yaml(path, contents):
    with open(path, 'w', encoding="utf-8") as fp:
        yaml.dump(contents, fp , Dumper=NoAliasDumper, allow_unicode=True, sort_keys=False )

def load_light():
    yaml_path  = __file__.replace("/scan.py","") + "/lights1.yaml"
    if os.path.exists(yaml_path):
        lights = _open_yaml(yaml_path)
        for light, data in lights.items():
            data["id_v1"] = light
            lightObject[light] = Light.Light(data)
        return lightObject
    else:
        logging.debug("lights.yaml not found")

#discover.py
def nextFreeId():
    i = 1
    while (str(i)) in lightObject:
        i += 1
    return str(i)

def pretty_json(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

def scanHost(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Very short timeout. If scanning fails this could be increased
    sock.settimeout(0.02)
    result = sock.connect_ex((host, port))
    sock.close()
    return result


def iter_ips(port):
    HOST_IP = "192.168.1.3"
    scan_on_host_ip = False
    ip_range_start = 0
    ip_range_end = 255
    sub_ip_range_start = 1
    sub_ip_range_end = 1
    host = HOST_IP.split('.')
    if scan_on_host_ip:
        yield ('127.0.0.1', port)
    for sub_addr in range(sub_ip_range_start, sub_ip_range_end + 1):
        host[2] = str(sub_addr)
        for addr in range(ip_range_start, ip_range_end + 1):
            host[3] = str(addr)
            test_host = '.'.join(host)
            if test_host != HOST_IP:
                yield (test_host, port)


def find_hosts(port):
    validHosts = []
    for host, port in iter_ips(port):
        if scanHost(host, port) == 0:
            hostWithPort = '%s:%s' % (host, port)
            validHosts.append(hostWithPort)

    return validHosts

def addNewLight(modelid, name, protocol, protocol_cfg):
    newLightID = nextFreeId()
    if modelid in lightTypes:
        light = lightTypes[modelid]
        light["name"] = name
        light["id_v1"] = newLightID
        light["modelid"] = modelid
        light["protocol"] = protocol
        light["protocol_cfg"] = protocol_cfg
        newObject = Light.Light(light)
        lightObject[newLightID] = newObject

        return newLightID
    return False

def scanForLights():  # scan for ESP8266 lights and strips
    device_ips = find_hosts(80)
    logging.info(pretty_json(device_ips))
    detectedLights = []
    
    WledDevice.discover(detectedLights, device_ips)

    for light in detectedLights:
        # check if light is already present
        lightIsNew = True
        for key, lightObj in lightObject.items():
            if lightObj.protocol == light["protocol"]:
                if light["protocol"] in ["wled"]:
                    # Check based on mac and segment and modelid
                    if lightObj.protocol_cfg["mac"] == light["protocol_cfg"]["mac"] and lightObj.protocol_cfg["segmentId"] == light["protocol_cfg"]["segmentId"] and lightObj.modelid == light["modelid"]:
                        logging.info("Update IP for light " + light["name"])
                        lightObj.protocol_cfg["ip"] = light["protocol_cfg"]["ip"]
                        lightObj.protocol_cfg["ledCount"] = light["protocol_cfg"]["ledCount"]
                        lightObj.protocol_cfg["segment_start"] = light["protocol_cfg"]["segment_start"]
                        lightObj.protocol_cfg["udp_port"] = light["protocol_cfg"]["udp_port"]
                        lightIsNew = False
        if lightIsNew:
            logging.info("Add new light " + light["name"])
            lightId = addNewLight(light["modelid"], light["name"], light["protocol"], light["protocol_cfg"])
