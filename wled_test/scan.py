import wled
import native_multi
import logManager
from light_types import lightTypes
import Light
import os
import yaml
import socket
import json
import hue
import govee

logging = logManager.logger.get_logger(__name__)

bridgeConfig_Light = {}

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

def load_light(file):
    yaml_path  = __file__.replace("scan.py", file)
    if os.path.exists(yaml_path):
        lights = _open_yaml(yaml_path)
        for light, data in lights.items():
            data["id_v1"] = light
            bridgeConfig_Light[light] = Light.Light(data)
        return bridgeConfig_Light
    else:
        logging.debug("lights.yaml not found")

def save_lights(file):
    yaml_path  = __file__.replace("scan.py", file)
    dumpDict = {}
    for element in bridgeConfig_Light:
        if element != "0":
            savedData = bridgeConfig_Light[element].save()
            if savedData:
                dumpDict[bridgeConfig_Light[element].id_v1] = savedData
    _write_yaml(yaml_path, dumpDict)

#discover.py
def nextFreeId():
    i = 1
    while (str(i)) in bridgeConfig_Light:
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
        bridgeConfig_Light[newLightID] = newObject

        return newLightID
    return False

def scanForLights():  # scan for ESP8266 lights and strips
    device_ips = []
    for ports in [80, 81]:
        # return all host that listen on ports in list config
        device_ips += find_hosts(ports)
    logging.info(pretty_json(device_ips))
    detectedLights = []
    
    #native_multi.discover(detectedLights, device_ips)
    #wled.discover(detectedLights, device_ips)
    #hue.discover(detectedLights, hueUser="", ip="")
    govee.discover(detectedLights)

    for light in detectedLights:
        # check if light is already present
        lightIsNew = True
        for key, lightObj in bridgeConfig_Light.items():
            if lightObj.protocol == light["protocol"]:
                if light["protocol"] == "native_multi":
                    # check based on mac address and modelid
                    if lightObj.protocol_cfg["mac"] == light["protocol_cfg"]["mac"] and lightObj.protocol_cfg["light_nr"] == light["protocol_cfg"]["light_nr"] and lightObj.modelid == light["modelid"]:
                        logging.info("Update IP for light " + light["name"])
                        lightObj.protocol_cfg["ip"] = light["protocol_cfg"]["ip"]
                        lightIsNew = False
                        break
                elif light["protocol"] in ["hue", "deconz"]:
                    # check based on light uniqueid and modelid
                    if lightObj.protocol_cfg["uniqueid"] == light["protocol_cfg"]["uniqueid"]  and lightObj.modelid == light["modelid"]:
                        logging.info("Update IP for light " + light["name"])
                        lightObj.protocol_cfg["ip"] = light["protocol_cfg"]["ip"]
                        lightIsNew = False
                elif light["protocol"] in ["wled"]:
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
            #logging.info(f"New light added with id {int(lightId)}")
