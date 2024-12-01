import logManager
from scan import scanForLights, load_light, _write_yaml, bridgeConfig_Light
import WledDevice
import native_multi
import socket
import random
from time import sleep, time
from colors import convert_rgb_xy

logging = logManager.logger.get_logger(__name__)

def save_lights():
    yaml_path  = __file__.replace("/wled_test.py","") + "/lights1.yaml"
    dumpDict = {}
    for element in bridgeConfig_Light:
        if element != "0":
            savedData = bridgeConfig_Light[element].save()
            if savedData:
                dumpDict[bridgeConfig_Light[element].id_v1] = savedData
    _write_yaml(yaml_path, dumpDict)

#entertainment.py
wledLights = {}
nativeLights = {}
def run_entertainment():
    frameID = 0
    prev_frame_time = 0
    new_frame_time = 0
    prev_frameID = 0
    while frameID < 200000:
        #sleep(0.5)
        frameID += 1
        for key, light in bridgeConfig_Light.items():
            proto = light.protocol
            #if key in ["7"]:
            #    continue
            r = random.randrange(0, 255)#255
            g = random.randrange(0, 255)#127
            b = random.randrange(0, 255)#9
            #logging.debug(light.protocol_cfg)
            if proto in ["native", "native_multi", "native_single"]:
                if light.modelid == "LST002":
                    if light.protocol_cfg["ip"] not in nativeLights:
                        nativeLights[light.protocol_cfg["ip"]] = {}
                    nativeLights[light.protocol_cfg["ip"]][light.protocol_cfg["light_nr"] - 1] = [r, g, b]

            elif proto == "wled":
                if light.protocol_cfg["ip"] not in wledLights:
                    wledLights[light.protocol_cfg["ip"]] = {}
                if light.protocol_cfg["segmentId"] not in wledLights[light.protocol_cfg["ip"]]:
                    wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]] = {}
                    wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["ledCount"] = light.protocol_cfg["ledCount"]
                    wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["start"] = light.protocol_cfg["segment_start"]
                    wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["udp_port"] = light.protocol_cfg["udp_port"]
                    #logging.debug(wledLights)
                wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["color"] = [r, g, b]

        if len(nativeLights) != 0:
            for ip in nativeLights.keys():
                udpmsg = bytearray()
                for light in nativeLights[ip].keys():
                    udpmsg += bytes([light]) + bytes([nativeLights[ip][light][0]]) + bytes([nativeLights[ip][light][1]]) + bytes([nativeLights[ip][light][2]])
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
                sock.sendto(udpmsg, (ip.split(":")[0], 2100))

        if len(wledLights) != 0:
            wled_udpmode = 4 #DNRGB mode
            wled_secstowait = 2
            for ip in wledLights.keys():
                #logging.debug(ip.split(":")[0])
                for segments in wledLights[ip]:
                    #logging.debug(wledLights[ip][segments])
                    udphead = bytes([wled_udpmode, wled_secstowait])
                    start_seg = wledLights[ip][segments]["start"].to_bytes(2,"big")
                    color = bytes(wledLights[ip][segments]["color"] * int(wledLights[ip][segments]["ledCount"]))
                    udpdata = udphead+start_seg+color
                    #logging.debug(wledLights[ip][segments]["udp_port"])
                    #logging.debug(udpdata)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(udpdata, (ip.split(":")[0], wledLights[ip][segments]["udp_port"]))
        new_frame_time = time()
        if new_frame_time - prev_frame_time > 1:
            fps = frameID - prev_frameID
            prev_frame_time = new_frame_time
            prev_frameID = frameID
            logging.info("Entertainment FPS: " + str(fps))

def set_wled():
    r = random.randrange(0, 255)#255
    g = random.randrange(0, 255)#127
    b = random.randrange(0, 255)#9
    light_nr = 4
    light = bridgeConfig_Light[str(light_nr)]
    data = {"object": light, "lights": {light.protocol_cfg["segmentId"]: {"on": True, "bri":254, "xy": convert_rgb_xy(r, g, b)}}}
    WledDevice.set_light(light, data)

def get_wled():
    light_nr = 4
    light = bridgeConfig_Light[str(light_nr)]
    logging.debug(WledDevice.get_light_state(light))

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

#run_entertainment()
#set_wled()
#get_wled()
#set_native()
#get_native()
