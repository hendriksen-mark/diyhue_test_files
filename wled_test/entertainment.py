import logManager
from scan import bridgeConfig_Light
import socket
import random
from time import sleep, time
from colors import convert_rgb_xy, convert_xy

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

def run_entertainment():
    stream_data = []
    for data_i in range(len(bridgeConfig_Light)*10):
        stream_data.append(b'HueStream\x02\x009\x00\x00\x00\x0096a51e21-20db-562d-b565-13bb59c1a6a1\x00\xb4\xe7\xb9P\xff\xff\x01\x84\x84\x84\x83\x88\x8a\x02{\x8c\xab\xc4\xac\xaf\x03xy|\x90\x84b\x04\x9c\xc3\xa8\x83\xac\xda\x05\xa8\xa8\xb0\xaa\xbc\xc0\x06\xa8\xa8\xb0\xaa\xbc\xc0\x07\xa8\xa8\xb0\xaa\xbc\xc0')
    #logging.debug(stream_data)
    stream_active = True
    lights_v2 = []
    lights_v1 = {}
    hueGroupLights = {}
    prev_frame_time = 0
    new_frame_time = 0
    prev_frameID = 0
    non_UDP_update_counter = 0
    v2LightNr = {}
    for channel in bridgeConfig_Light:
        lightObj =  bridgeConfig_Light[channel]
        if lightObj.id_v1 not in v2LightNr:
            v2LightNr[lightObj.id_v1] = 0
        else:
            v2LightNr[lightObj.id_v1] += 1
        lights_v2.append({"light": lightObj, "lightNr": v2LightNr[lightObj.id_v1]})
    #logging.debug(lights_v1)
    #logging.debug(lights_v2)
    frameID = 1
    dataID = 0
    try:
        while stream_active:
            try:
                data = stream_data[dataID]
            except Exception as e: #Assuming the only exception is a network timeout, please don't scream at me
                logging.error("stream_data[" + str(dataID) + "] " + str(e))
                stream_active = False
                return
            dataID += 1
            #logging.debug(dataID)
            #logging.debug(data)
            #logging.debug(",".join('{:02x}'.format(x) for x in data))
            nativeLights = {}
            esphomeLights = {}
            wledLights = {}
            non_UDP_lights = []
            if data[:9].decode('utf-8') == "HueStream":
                i = 0
                apiVersion = 0
                counter = 0
                if data[9] == 1: #api version 1
                    i = 16
                    apiVersion = 1
                    counter = len(data)
                elif data[9] == 2: #api version 1
                    i = 52
                    apiVersion = 2
                    counter = len(bridgeConfig_Light) * 7 + 52
                channels = {}
                while (i < counter):
                    light = None
                    r,g,b = 0,0,0
                    bri = 0
                    if apiVersion == 1:
                        if (data[i+1] * 256 + data[i+2]) in channels:
                            channels[data[i+1] * 256 + data[i+2]] += 1
                        else:
                            channels[data[i+1] * 256 + data[i+2]] = 0
                        if data[i] == 0:  # Type of device 0x00 = Light
                            if data[i+1] * 256 + data[i+2] == 0:
                                break
                            light = lights_v1[data[i+1] * 256 + data[i+2]]
                        if data[14] == 0: #rgb colorspace
                            r = int((data[i+3] * 256 + data[i+4]) / 256)
                            g = int((data[i+5] * 256 + data[i+6]) / 256)
                            b = int((data[i+7] * 256 + data[i+8]) / 256)
                        elif data[14] == 1: #cie colorspace
                            x = (data[i+3] * 256 + data[i+4]) / 65535
                            y = (data[i+5] * 256 + data[i+6]) / 65535
                            bri = int((data[i+7] * 256 + data[i+8]) / 256)
                            r, g, b = convert_xy(x, y, bri)
                    elif apiVersion == 2:
                        light = lights_v2[data[i]]["light"]
                        if data[14] == 0: #rgb colorspace
                            r = random.randrange(0, 255)#255
                            g = random.randrange(0, 255)#127
                            b = random.randrange(0, 255)#9
                            #r = int((data[i+1] * 256 + data[i+2]) / 256)
                            #g = int((data[i+3] * 256 + data[i+4]) / 256)
                            #b = int((data[i+5] * 256 + data[i+6]) / 256)
                        elif data[14] == 1: #cie colorspace
                            x = (data[i+1] * 256 + data[i+2]) / 65535
                            y = (data[i+3] * 256 + data[i+4]) / 65535
                            bri = int((data[i+5] * 256 + data[i+6]) / 256)
                            r, g, b = convert_xy(x, y, bri)
                    if light == None:
                        logging.info("error in light identification")
                        break
                    #logging.debug("Frame: " + str(frameID) + " Light:" + str(light.name) + " RED: " + str(r) + ", GREEN: " + str(g) + ", BLUE: " + str(b) )
                    proto = light.protocol
                    if r == 0 and  g == 0 and  b == 0:
                        light.state["on"] = False
                    else:
                        if bri == 0:
                            light.state.update({"on": True, "bri": int((r + g + b) / 3), "xy": convert_rgb_xy(r, g, b), "colormode": "xy"})
                        else:
                            light.state.update({"on": True, "bri": bri, "xy": [x, y], "colormode": "xy"})
                        #logging.debug("in X: " + str(x) + " Y: " + str(y) + " B: " + str(bri))
                        #logging.debug("st X: " + str(light.state["xy"][0]) + " Y: " + str(light.state["xy"][1]) + " B: " + str(light.state["bri"]))
                        #logging.debug("co XY: " + str(convert_rgb_xy(r, g, b)) + " B: " + str((r + g + b) / 3))
                    if proto in ["native", "native_multi", "native_single"]:
                        if light.protocol_cfg["ip"] not in nativeLights:
                            nativeLights[light.protocol_cfg["ip"]] = {}
                        if apiVersion == 1:
                            if light.modelid in ["LCX001", "LCX002", "LCX003", "915005987201", "LCX004"]:
                                if data[i] == 1: # individual strip address
                                    nativeLights[light.protocol_cfg["ip"]][data[i+1] * 256 + data[i+2]] = [r, g, b]
                                elif data[i] == 0: # individual strip address
                                    for x in range(7):
                                        nativeLights[light.protocol_cfg["ip"]][x] = [r, g, b]
                            else:
                                nativeLights[light.protocol_cfg["ip"]][light.protocol_cfg["light_nr"] - 1] = [r, g, b]

                        elif apiVersion == 2:
                            if light.modelid in ["LCX001", "LCX002", "LCX003", "915005987201", "LCX004"]:
                                nativeLights[light.protocol_cfg["ip"]][lights_v2[data[i]]["lightNr"]] = [r, g, b]
                            else:
                                nativeLights[light.protocol_cfg["ip"]][light.protocol_cfg["light_nr"] - 1] = [r, g, b]
                    elif proto == "esphome":
                        if light.protocol_cfg["ip"] not in esphomeLights:
                            esphomeLights[light.protocol_cfg["ip"]] = {}
                        bri = int(max(r,g,b))
                        esphomeLights[light.protocol_cfg["ip"]]["color"] = [r, g, b, bri]
                    elif proto == "wled":
                        if light.protocol_cfg["ip"] not in wledLights:
                            wledLights[light.protocol_cfg["ip"]] = {}
                        if light.protocol_cfg["segmentId"] not in wledLights[light.protocol_cfg["ip"]]:
                            wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]] = {}
                            wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["ledCount"] = light.protocol_cfg["ledCount"]
                            wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["start"] = light.protocol_cfg["segment_start"]
                            wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["udp_port"] = light.protocol_cfg["udp_port"]
                        wledLights[light.protocol_cfg["ip"]][light.protocol_cfg["segmentId"]]["color"] = [r, g, b]
                    elif proto == "hue" and int(light.protocol_cfg["id"]) in hueGroupLights:
                        hueGroupLights[int(light.protocol_cfg["id"])] = [r,g,b]
                    else:
                        if light not in non_UDP_lights:
                            non_UDP_lights.append(light)

                    frameID += 1
                    if apiVersion == 1:
                        i = i + 9
                    elif  apiVersion == 2:
                        i = i + 7

                if len(nativeLights) != 0:
                    for ip in nativeLights.keys():
                        udpmsg = bytearray()
                        for light in nativeLights[ip].keys():
                            udpmsg += bytes([light]) + bytes([nativeLights[ip][light][0]]) + bytes([nativeLights[ip][light][1]]) + bytes([nativeLights[ip][light][2]])
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
                        sock.sendto(udpmsg, (ip.split(":")[0], 2100))
                if len(esphomeLights) != 0:
                    for ip in esphomeLights.keys():
                        udpmsg = bytearray()
                        udpmsg += bytes([0]) + bytes([esphomeLights[ip]["color"][0]]) + bytes([esphomeLights[ip]["color"][1]]) + bytes([esphomeLights[ip]["color"][2]]) + bytes([esphomeLights[ip]["color"][3]])
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
                    #logging.debug(len(non_UDP_lights))#=8
                    logging.debug(non_UDP_update_counter)
                    light = non_UDP_lights[non_UDP_update_counter]
                    operation = skipSimilarFrames(light.id_v1, light.state["xy"], light.state["bri"])
                    if operation == 1:
                        light.setV1State({"bri": light.state["bri"], "transitiontime": 3})
                    elif operation == 2:
                        light.setV1State({"xy": light.state["xy"], "transitiontime": 3})
                    non_UDP_update_counter = non_UDP_update_counter + 1 if non_UDP_update_counter < len(non_UDP_lights)-1 else 0

                new_frame_time = time()
                if new_frame_time - prev_frame_time > 1:
                    fps = frameID - prev_frameID
                    prev_frame_time = new_frame_time
                    prev_frameID = frameID
                    #logging.info("Entertainment FPS: " + str(fps))
            else:
                logging.info("HueStream was missing in the frame")
    except Exception as e: #Assuming the only exception is a network timeout, please don't scream at me
        logging.error("Entertainment Service was syncing and has timed out, stopping server and clearing state " + str(e))
    stream_active = False
    logging.info("Entertainment service stopped")