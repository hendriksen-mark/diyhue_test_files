import logManager
from configHandler import load_light, save_lights, bridgeConfig_Light
from discover import scanForLights
from random import randrange
from colors import convert_rgb_xy
from entertainment import run_entertainment
from stateFetch import syncWithLights

logging = logManager.logger.get_logger(__name__)

#logManager.logger.configure_logger("INFO")

def set_light():
    r = randrange(0, 255)#255
    g = randrange(0, 255)#127
    b = randrange(0, 255)#9
    light_nr = 1
    light = bridgeConfig_Light[str(light_nr)]
    light.setV1State({"on": True, "bri": 255, "transitiontime": 4, "xy": convert_rgb_xy(r, g, b), "colormode": "xy"})

def get_light():
    light_nr = 24
    light = bridgeConfig_Light[str(light_nr)]
    logging.debug(light.getV1Api())

load_light("lights6.yaml")
#for light in bridgeConfig_Light:
    #logging.debug(bridgeConfig_Light[light].protocol_cfg)

scanForLights()
#for light in bridgeConfig_Light:
#    logging.debug(bridgeConfig_Light[light].get_info())

save_lights("lights6.yaml")

#run_entertainment()
#set_light()
#get_light()
#syncWithLights(False)
#save_lights("lights6.yaml")
