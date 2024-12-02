import logManager
from scan import scanForLights, load_light, save_lights, bridgeConfig_Light
import random
from colors import convert_rgb_xy
from entertainment import run_entertainment

logging = logManager.logger.get_logger(__name__)

def set_light():
    r = random.randrange(0, 255)#255
    g = random.randrange(0, 255)#127
    b = random.randrange(0, 255)#9
    light_nr = 24
    light = bridgeConfig_Light[str(light_nr)]
    light.setV1State({"on": True, "bri": 254, "transitiontime": 4, "xy": convert_rgb_xy(r, g, b), "colormode": "xy"})

def get_light():
    light_nr = 24
    light = bridgeConfig_Light[str(light_nr)]
    logging.debug(light.getV1Api())

load_light("/lights1.yaml")
#for light in bridgeConfig_Light:
#    logging.debug(bridgeConfig_Light[light].protocol_cfg)

#scanForLights()
#for light in bridgeConfig_Light:
#    logging.debug(bridgeConfig_Light[light].protocol_cfg)

#save_lights("/lights2.yaml")

run_entertainment()
#set_light()
#get_light()
