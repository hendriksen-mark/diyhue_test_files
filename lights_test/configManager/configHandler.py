import logManager
import HueObjects.Light as Light
import os
import yaml

logging = logManager.logger.get_logger(__name__)

bridgeConfig_Light = {}

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
    yaml_path  = __file__.replace("configManager/configHandler.py", "config/" + file)
    if os.path.exists(yaml_path):
        lights = _open_yaml(yaml_path)
        for light, data in lights.items():
            data["id_v1"] = light
            bridgeConfig_Light[light] = Light.Light(data)
        return bridgeConfig_Light
    else:
        logging.debug(f"{file} not found")

def save_lights(file):
    yaml_path  = __file__.replace("configManager/configHandler.py", "config/" + file)
    dumpDict = {}
    for element in bridgeConfig_Light:
        if element != "0":
            savedData = bridgeConfig_Light[element].save()
            if savedData:
                dumpDict[bridgeConfig_Light[element].id_v1] = savedData
    _write_yaml(yaml_path, dumpDict)