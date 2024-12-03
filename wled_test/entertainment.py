import logManager
from scan import bridgeConfig_Light
import socket
import random
from time import sleep, time
from colors import convert_rgb_xy

logging = logManager.logger.get_logger(__name__)

cieTolerance = 0.03 # new frames will be ignored if the color  change is smaller than this values
briTolerange = 16 # new frames will be ignored if the brightness change is smaller than this values
lastAppliedFrame = {}

def skipSimilarFrames(light, color, brightness):
    if light not in lastAppliedFrame: # check if light exist in dictionary
        lastAppliedFrame[light] = {"xy": [0,0], "bri": 0}

    if lastAppliedFrame[light]["xy"][0] + cieTolerance < color[0] or color[0] < lastAppliedFrame[light]["xy"][0] - cieTolerance:
        lastAppliedFrame[light]["xy"] = color
        return 2
    if lastAppliedFrame[light]["xy"][1] + cieTolerance < color[1] or color[1] < lastAppliedFrame[light]["xy"][1] - cieTolerance:
        lastAppliedFrame[light]["xy"] = color
        return 2
    if lastAppliedFrame[light]["bri"] + briTolerange < brightness or brightness < lastAppliedFrame[light]["bri"] - briTolerange:
        lastAppliedFrame[light]["bri"] = brightness
        return 1
    return 0

wledLights = {}
nativeLights = {}
non_UDP_lights = {}
def run_entertainment():
    frameID = 0
    prev_frame_time = 0
    new_frame_time = 0
    prev_frameID = 0
    while frameID < 200:
        #sleep(0.5)
        for key, light in bridgeConfig_Light.items():
            r = random.randrange(0, 255)#255
            g = random.randrange(0, 255)#127
            b = random.randrange(0, 255)#9
            bri = 254
            x, y = convert_rgb_xy(r, g, b)

            proto = light.protocol

            if r == 0 and  g == 0 and  b == 0:
                light.state["on"] = False
            else:
                if bri == 0:
                    light.state.update({"on": True, "bri": int((r + g + b) / 3), "xy": convert_rgb_xy(r, g, b), "colormode": "xy"})
                else:
                    light.state.update({"on": True, "bri": bri, "xy": [x, y], "colormode": "xy"})
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
                wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["color"] = [r, g, b]
            
            else:
                if key not in non_UDP_lights.keys and non_UDP_lights[key] != light:
                    #non_UDP_lights[light.id_v1] = light
                    non_UDP_lights[key] = light

            frameID += 1

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
                for segments in wledLights[ip]:
                    udphead = bytes([wled_udpmode, wled_secstowait])
                    start_seg = wledLights[ip][segments]["start"].to_bytes(2,"big")
                    color = bytes(wledLights[ip][segments]["color"] * int(wledLights[ip][segments]["ledCount"]))
                    udpdata = udphead+start_seg+color
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(udpdata, (ip.split(":")[0], wledLights[ip][segments]["udp_port"]))

        if len(non_UDP_lights) != 0:
            logging.debug(non_UDP_lights)
            #light = non_UDP_lights[frameID % len(non_UDP_lights)]
            #operation = skipSimilarFrames(light.id_v1, light.state["xy"], light.state["bri"])
            #if operation == 1:
            #    light.setV1State({"bri": light.state["bri"], "transitiontime": 3})
            #elif operation == 2:
            #    light.setV1State({"xy": light.state["xy"], "transitiontime": 3})
        #logging.debug(frameID)

        new_frame_time = time()
        if new_frame_time - prev_frame_time > 1:
            fps = frameID - prev_frameID
            prev_frame_time = new_frame_time
            prev_frameID = frameID
            logging.info("Entertainment FPS: " + str(fps))
