import logManager
from scan import scanForLights, load_light

logging = logManager.logger.get_logger(__name__)

r = 255
g = 127
b = 9

lights = load_light()
#for light in lights:
#    logging.debug(light.protocol_cfg)
#lights = scanForLights()
wledLights = {}

for light in lights:
    #logging.debug(light.protocol_cfg)

    if light.protocol_cfg["ip"] not in wledLights:
        wledLights[light.protocol_cfg["ip"]] = {}
    if light.protocol_cfg["segmentId"] not in wledLights[light.protocol_cfg["ip"]]:
        wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]] = {}
        wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["ledCount"] = light.protocol_cfg["ledCount"]
        wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["start"] = light.protocol_cfg["segment_start"]
    wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["color"] = [r, g, b]

#logging.debug(wledLights)

wled_udpmode = 4 #DNRGB mode
wled_secstowait = 2
for ip in wledLights.keys():
    #logging.debug(ip)
    for segments in wledLights[ip]:
        #logging.debug(wledLights[ip][segments])
        udphead = bytes([wled_udpmode, wled_secstowait])
        start_seg = wledLights[ip][segments]["start"].to_bytes(2,"big")
        color = bytes(wledLights[ip][segments]["color"] * int(wledLights[ip][segments]["ledCount"]))
        udpdata = udphead+start_seg+color
        #logging.debug(udpdata)
