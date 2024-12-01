import logManager
from scan import scanForLights, load_light, _write_yaml, nextFreeId, lightObject
import WledDevice
import socket
import random
from time import sleep, time
from colors import convert_rgb_xy

logging = logManager.logger.get_logger(__name__)

def save_lights():
    yaml_path  = __file__.replace("/wled_test.py","") + "/lights1.yaml"
    dumpDict = {}
    for element in lightObject:
        if element != "0":
            savedData = lightObject[element].save()
            if savedData:
                dumpDict[lightObject[element].id_v1] = savedData
    _write_yaml(yaml_path, dumpDict)

#entertainment.py
wledLights = {}
nativeLights = {}
apiVersion = 2
def run_entertainment():
    frameID = 0
    prev_frame_time = 0
    new_frame_time = 0
    prev_frameID = 0
    i = 0
    while i < 200000:
        #sleep(0.5)
        frameID += 1
        i += 1
        for key, light in lightObject.items():
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
    convert_rgb_xy(r, g, b)
    light_nr = 4
    light = lightObject[str(light_nr)]
    data = {"object": light, "lights": {light.protocol_cfg["segmentId"]: {"on": False, "bri":254, "xy": convert_rgb_xy(r, g, b)}}}
    WledDevice.set_light(light, data)

def get_light():
    light_nr = 4
    light = lightObject[str(light_nr)]
    logging.debug(WledDevice.get_light_state(light))

load_light()
#for light in lightObject:
#    logging.debug(lightObject[light].protocol_cfg)

#scanForLights()
#for light in lightObject:
#    logging.debug(lightObject[light].protocol_cfg)

#i = 0
#while i < 2000:
run_entertainment()
    #sleep(0.05)
#    i += 1
#save_lights()
#set_wled()
#findLights()
#get_light()
