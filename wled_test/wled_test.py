import logManager
from scan import scanForLights, load_light, save_lights, _write_yaml, bridgeConfig_Light
import wled
import native_multi
import random
from time import sleep, time
from colors import convert_rgb_xy
from entertainment import run_entertainment

logging = logManager.logger.get_logger(__name__)

def set_wled():
    r = random.randrange(0, 255)#255
    g = random.randrange(0, 255)#127
    b = random.randrange(0, 255)#9
    light_nr = 4
    light = bridgeConfig_Light[str(light_nr)]
    data = {"object": light, "lights": {light.protocol_cfg["segmentId"]: {"on": True, "bri":254, "xy": convert_rgb_xy(r, g, b)}}}
    wled.set_light(light, data)

def get_wled():
    light_nr = 4
    light = bridgeConfig_Light[str(light_nr)]
    logging.debug(wled.get_light_state(light))

def set_native():
    r = random.randrange(0, 255)#255
    g = random.randrange(0, 255)#127
    b = random.randrange(0, 255)#9
    light_nr = 24
    light = bridgeConfig_Light[str(light_nr)]
    data = {"object": light, "lights": {light.protocol_cfg["light_nr"]: {"on": True, "bri":254, "xy": convert_rgb_xy(r, g, b)}}}
    native_multi.set_light(light, data)

def get_native():
    light_nr = 24
    light = bridgeConfig_Light[str(light_nr)]
    logging.debug(native_multi.get_light_state(light))

load_light()
#for light in bridgeConfig_Light:
#    logging.debug(bridgeConfig_Light[light].protocol_cfg)

#scanForLights()
#for light in bridgeConfig_Light:
#    logging.debug(bridgeConfig_Light[light].protocol_cfg)

#save_lights()

run_entertainment()
#set_wled()
#get_wled()
#set_native()
#get_native()
