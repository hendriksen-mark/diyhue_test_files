import WledDevice
import logManager
from light_types import lightTypes
import Light
import os
import yaml
import pathlib

logging = logManager.logger.get_logger(__name__)

#configHandler.py
def reAddWled(old_light):
    #logging.debug(old_light["protocol_cfg"])
    detectedLights = []
    WledDevice.discover(detectedLights, old_light["protocol_cfg"]["ip"])
    for light in detectedLights:
        #logging.debug(light)
        if light["name"] == old_light["name"] and light["protocol_cfg"]["ip"] == old_light["protocol_cfg"]["ip"] and light["protocol_cfg"]["segmentId"] == old_light["protocol_cfg"]["segmentId"]:
            logging.info("Update Wled " + light["name"])
            #logging.debug(old_light["protocol_cfg"])
            old_light["protocol_cfg"]["ledCount"] = light["protocol_cfg"]["ledCount"]
            old_light["protocol_cfg"]["segment_start"] = light["protocol_cfg"]["segment_start"]
            old_light["protocol_cfg"]["udp_port"] = light["protocol_cfg"]["udp_port"]
            #logging.debug(old_light["protocol_cfg"])
            return old_light

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
    lightObject = []
    yaml_path  = __file__.replace("/scan.py","") + "/lights1.yaml"
    #logging.debug(yaml_path)
    if os.path.exists(yaml_path):
        #logging.debug("found lights.yaml")
        lights = _open_yaml(yaml_path)
        for light, data in lights.items():
            #logging.debug(light)
            #logging.debug(data["protocol"])
            if data["protocol"] == "wled" and "segment_start" not in data["protocol_cfg"]:
                data = reAddWled(data)
            data["id_v1"] = light
            lightObject.append(Light.Light(data))
        return lightObject
    else:
        logging.debug("lights.yaml not found")

#discover.py
def addNewLight(modelid, name, protocol, protocol_cfg):
    newLightID = 1
    if modelid in lightTypes:
        light = lightTypes[modelid]
        light["name"] = name
        light["id_v1"] = newLightID
        light["modelid"] = modelid
        light["protocol"] = protocol
        light["protocol_cfg"] = protocol_cfg
        newObject = Light.Light(light)

        return newObject
    return False

def scanForLights():  # scan for ESP8266 lights and strips
    detectedLights = []
    lightObject = []
    
    WledDevice.discover(detectedLights)

    for light in detectedLights:
        # check if light is already present
        lightIsNew = True
        if lightIsNew:
            logging.info("Add new light " + light["name"])
            lightObject.append(addNewLight(light["modelid"], light["name"], light["protocol"], light["protocol_cfg"]))
    return lightObject