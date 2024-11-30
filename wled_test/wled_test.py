import logManager
from scan import scanForLights, load_light, _write_yaml
import WledDevice

logging = logManager.logger.get_logger(__name__)

lights = load_light()
#for light in lights:
#    logging.debug(light.protocol_cfg)
#lights = scanForLights()

def findLights():
    new_lights = scanForLights(lights)
    for light in new_lights:
        logging.debug(light.protocol_cfg)
    lights.append(new_lights)

def save_lights():
    yaml_path  = __file__.replace("/wled_test.py","") + "/lights1.yaml"
    dumpDict = {}
    for element in lights:
        if element != "0":
            savedData = element.save()
            if savedData:
                dumpDict[element.id_v1] = savedData
    _write_yaml(yaml_path, dumpDict)

#entertainment.py
def run_entertainment():
    r = 255
    g = 127
    b = 9
    wledLights = {}

    for light in lights:
        #logging.debug(light.protocol_cfg)

        if light.protocol_cfg["ip"] not in wledLights:
            wledLights[light.protocol_cfg["ip"]] = {}
        if light.protocol_cfg["segmentId"] not in wledLights[light.protocol_cfg["ip"]]:
            wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]] = {}
            wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["ledCount"] = light.protocol_cfg["ledCount"]
            wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["start"] = light.protocol_cfg["segment_start"]
            wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["udp_port"] = light.protocol_cfg["udp_port"]
        wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["color"] = [r, g, b]

    #logging.debug(wledLights)

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

def set_wled():
    light_nr = 1
    light = lights[light_nr]
    data = {"object": light, "lights": {light_nr: {"on": True, "bri":254}}}
    WledDevice.set_light(light, data)

#run_entertainment()
#save_lights()
#set_wled()
findLights()
