import logManager
from configManager.configHandler import load_light, save_lights, bridgeConfig_Light
from lights.discover import scanForLights
from random import randrange
from functions.colors import convert_rgb_xy
from services.entertainment import run_entertainment
from services.stateFetch import syncWithLights

logging = logManager.logger.get_logger(__name__)

#logManager.logger.configure_logger("INFO")

def set_light():
    for light_nr in range(1, 2):
        light = bridgeConfig_Light[str(light_nr)]
        #light.setV1State({"on": True, "bri": 255, "transitiontime": 4, "xy": convert_rgb_xy(randrange(0, 255), randrange(0, 255), randrange(0, 255)), "colormode": "xy"})
        light.setV1State({"bri": 255})
        #light.setV1State({"xy": convert_rgb_xy(randrange(0, 255), randrange(0, 255), randrange(0, 255)), "colormode": "xy"})

def get_light():
    light_nr = 1
    light = bridgeConfig_Light[str(light_nr)]
    logging.debug(light.getV1Api())

#load_light("lights10.yaml")
#for light in bridgeConfig_Light:
    #logging.debug(bridgeConfig_Light[light].protocol_cfg)

scanForLights()
#for light in bridgeConfig_Light:
#    logging.debug(bridgeConfig_Light[light].get_info())

save_lights("lights12.yaml")

#run_entertainment()
#set_light()
#get_light()
#syncWithLights(False)
#save_lights("lights6.yaml")
