import logManager
from lights.discover import bridgeConfig_Light
import socket, json
import random
from time import sleep, time
from functions.colors import convert_rgb_xy, convert_xy
import requests
from subprocess import Popen, PIPE

logging = logManager.logger.get_logger(__name__)

cieTolerance = 0.03 # new frames will be ignored if the color  change is smaller than this values
briTolerange = 16 # new frames will be ignored if the brightness change is smaller than this values
lastAppliedFrame = {}
skip_light = "240"
num_runs = 10
stream_data_start = b'HueStream\x02\x00\x00\x00\x00\x00\x0096a51e21-20db-562d-b565-13bb59c1a6a1'
hue_entertainment_group = {}
hue_entertainment_group["hueUser"] = "a06c6df6bd8f11efb0a7acde48001122"
hue_entertainment_group["hueKey"] = "E43643EC486140C3BF80DD089F92BF20"
hue_entertainment_group["group_name"] = "TV-ruimte"
hue_entertainment_group["ip"] = "192.168.1.3"

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

def get_hue_entertainment_group(light, groupname):
    group = requests.get("http://" + light.protocol_cfg["ip"] + "/api/" + light.protocol_cfg["hueUser"] + "/groups/", timeout=3)
    #logging.debug("Returned Groups: " + group.text)
    groups = json.loads(group.text)
    out = -1
    for i, grp in groups.items():
        #logging.debug("Group "  + i + " has Name " + grp["name"] + " and type " + grp["type"])
        if (grp["name"] == groupname) and (grp["type"] == "Entertainment") and (light.protocol_cfg["id"] in grp["lights"]):
            out = i
            logging.debug("Found Corresponding entertainment group with id " + out + " for light " + light.name)
    return int(out)

def run_entertainment():
    stream_data = []
    for data_i in range(num_runs):
        color_data = bytes()
        for light_i in range(len(bridgeConfig_Light)):
            light = light_i.to_bytes(1,"big")
            r = random.randrange(0, 65535).to_bytes(2,"big")
            g = random.randrange(0, 65535).to_bytes(2,"big")
            b = random.randrange(0, 65535).to_bytes(2,"big")
            color_data += light+r+g+b
            #logging.debug(color_data)
        stream_data.append(stream_data_start+color_data)
    #logging.debug(stream_data)
    lights_v2 = []
    lights_v1 = {}
    hueGroup  = -1
    hueGroupLights = {}
    prev_frame_time = 0
    new_frame_time = 0
    non_UDP_update_counter = 0
    v2LightNr = {}
    for light in bridgeConfig_Light:
        lights_v1[int(light)] = bridgeConfig_Light[light]
        light = bridgeConfig_Light[light]
        if light.protocol == "hue" and get_hue_entertainment_group(light, hue_entertainment_group["group_name"]) != -1: # If the lights' Hue bridge has an entertainment group with the same name as this current group, we use it to sync the lights.
            hueGroup = get_hue_entertainment_group(light, hue_entertainment_group["group_name"])
            hueGroupLights[int(light.protocol_cfg["id"])] = [] # Add light id to list
        light.state["mode"] = "streaming"
        light.state["on"] = True
        light.state["colormode"] = "xy"
    for channel in bridgeConfig_Light:
        lightObj =  bridgeConfig_Light[channel]
        if lightObj.id_v1 not in v2LightNr:
            v2LightNr[lightObj.id_v1] = 0
        else:
            v2LightNr[lightObj.id_v1] += 1
        lights_v2.append({"light": lightObj, "lightNr": v2LightNr[lightObj.id_v1]})
    #logging.debug(lights_v1)
    #logging.debug(lights_v2)
    if hueGroup != -1:  # If we have found a hue Brige containing a suitable entertainment group for at least one Lamp, we connect to it
        h = HueConnection(hue_entertainment_group["ip"])
        h.connect(hueGroup, hueGroupLights)
        if h._connected == False:
            hueGroupLights = {} # on a failed connection, empty the list
    else:
        logging.info("no hue connection")
    frameID = 1
    dataID = 0
    try:
        while (dataID < len(stream_data)-1):
            new_frame_time = time()
            sleep(0.037)
            data = stream_data[dataID]
            dataID = dataID + 1
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
                            r = 0 if light.id_v1 == skip_light else int((data[i+3] * 256 + data[i+4]) / 256)
                            g = 0 if light.id_v1 == skip_light else int((data[i+5] * 256 + data[i+6]) / 256)
                            b = 0 if light.id_v1 == skip_light else int((data[i+7] * 256 + data[i+8]) / 256)
                        elif data[14] == 1: #cie colorspace
                            x = (data[i+3] * 256 + data[i+4]) / 65535
                            y = (data[i+5] * 256 + data[i+6]) / 65535
                            bri = int((data[i+7] * 256 + data[i+8]) / 256)
                            r, g, b = convert_xy(x, y, bri)
                    elif apiVersion == 2:
                        light = lights_v2[data[i]]["light"]
                        if data[14] == 0: #rgb colorspace
                            r = 0 if light.id_v1 == skip_light else int((data[i+1] * 256 + data[i+2]) / 256)
                            g = 0 if light.id_v1 == skip_light else int((data[i+3] * 256 + data[i+4]) / 256)
                            b = 0 if light.id_v1 == skip_light else int((data[i+5] * 256 + data[i+6]) / 256)
                        elif data[14] == 1: #cie colorspace
                            x = (data[i+1] * 256 + data[i+2]) / 65535
                            y = (data[i+3] * 256 + data[i+4]) / 65535
                            bri = int((data[i+5] * 256 + data[i+6]) / 256)
                            r, g, b = convert_xy(x, y, bri)
                            r = 0 if light.id_v1 == skip_light else r
                            g = 0 if light.id_v1 == skip_light else g
                            b = 0 if light.id_v1 == skip_light else b
                    if light == None:
                        logging.info("error in light identification")
                        break
                    logging.debug("Frame: " + str(frameID) + " Light:" + str(light.name) + " RED: " + str(r) + ", GREEN: " + str(g) + ", BLUE: " + str(b) )
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
                    if frameID == 25:
                        frameID = 1
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
                if len(hueGroupLights) != 0:
                        h.send(hueGroupLights, hueGroup)
                if len(non_UDP_lights) != 0:
                    light = non_UDP_lights[non_UDP_update_counter]
                    operation = skipSimilarFrames(light.id_v1, light.state["xy"], light.state["bri"])
                    if operation == 1:
                        light.setV1State({"bri": light.state["bri"], "transitiontime": 3})
                    elif operation == 2:
                        light.setV1State({"xy": light.state["xy"], "transitiontime": 3})
                    non_UDP_update_counter = non_UDP_update_counter + 1 if non_UDP_update_counter < len(non_UDP_lights)-1 else 0

                if new_frame_time - prev_frame_time > 1:
                    fps = 1.0 / (time() - new_frame_time)
                    prev_frame_time = new_frame_time
                    logging.info("Entertainment FPS: " + str(fps))
            else:
                logging.info("HueStream was missing in the frame")
    except Exception as e: #Assuming the only exception is a network timeout, please don't scream at me
        logging.error("Entertainment Service was syncing and has timed out, stopping server and clearing state " + str(e))
    for light in bridgeConfig_Light:
        light = bridgeConfig_Light[light]
        light.state["mode"] = "homeautomation"
    logging.info("Entertainment service stopped")

class HueConnection(object):
    _connected = False
    _ip = ""
    _entGroup = -1
    _connection = ""
    _hueLights = []

    def __init__(self, ip):
        self._ip = ip

    def connect(self, hueGroup, *lights):
        self._entGroup = hueGroup
        self._hueLights = lights
        self.disconnect()

        url = "HTTP://" + str(self._ip) + "/api/" + hue_entertainment_group["hueUser"] + "/groups/" + str(self._entGroup)
        r = requests.put(url, json={"stream":{"active":True}})
        logging.debug("Outgoing connection to hue Bridge returned: " + r.text)
        try:
            _opensslCmd = ['openssl', 's_client', '-quiet', '-cipher', 'PSK-AES128-GCM-SHA256', '-dtls', '-psk', hue_entertainment_group["hueKey"], '-psk_identity', hue_entertainment_group["hueUser"], '-connect', self._ip + ':2100']
            self._connection = Popen(_opensslCmd, stdin=PIPE, stdout=None, stderr=None) # Open a dtls connection to the Hue bridge
            self._connected = True
            sleep(1) # Wait a bit to catch errors
            err = self._connection.poll()
            if err != None:
                raise ConnectionError(err)
        except Exception as e:
            logging.info("Error connecting to Hue bridge for entertainment. Is a proper hueKey set? openssl connection returned: %s", e)
            self.disconnect()

    def disconnect(self):
        try:
            url = "HTTP://" + str(self._ip) + "/api/" + hue_entertainment_group["hueUser"] + "/groups/" + str(self._entGroup)
            if self._connected:
                self._connection.kill()
            requests.put(url, data={"stream":{"active":False}})
            self._connected = False
        except:
            pass

    def send(self, lights, hueGroup):
        arr = bytearray("HueStream", 'ascii')
        msg = [
                1, 0,     #Api version
                0,        #Sequence number, not needed
                0, 0,     #Zeroes
                0,        #0: RGB Color space, 1: XY Brightness
                0,        #Zero
              ]
        for id in lights:
            r, g, b = lights[id]
            msg.extend([    0,      #Type: Light
                            0, id,  #Light id (v1-type), 16 Bit
                            r, r,   #Red (or X) as 16 (2 * 8) bit value
                            g, g,   #Green (or Y)
                            b, b,   #Blue (or Brightness)
                            ])
        arr.extend(msg)
        #logging.debug(arr)
        logging.debug("Outgoing data to other Hue Bridge: " + str(arr))
        try:
            self._connection.stdin.write(arr)
            self._connection.stdin.flush()
        except:
            logging.debug("Reconnecting to Hue bridge to sync. This is normal.") #Reconnect if the connection timed out
            self.disconnect()
            self.connect(hueGroup)
