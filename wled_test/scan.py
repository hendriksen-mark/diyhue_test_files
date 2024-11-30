import WledData
import WledDevice
import logManager
from light_types import lightTypes
import Light

logging = logManager.logger.get_logger(__name__)

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