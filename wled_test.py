r = 255
g = 127
b = 9
wled = {
  "state": {
    "on": True,
    "bri": 127,
    "transition": 7,
    "ps": -1,
    "pl": -1,
    "nl": {
      "on": False,
      "dur": 60,
      "fade": True,
      "tbri": 0
    },
    "udpn": {
      "send": False,
      "recv": True
    },
    "seg": [
        {
            "start": 0,
            "stop": 19,
            "len": 20,
            "col": [
                [255, 160, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            "fx": 0,
            "sx": 127,
            "ix": 127,
            "pal": 0,
            "sel": True,
            "rev": False,
            "cln": -1
        },
        {
            "start": 21,
            "stop": 40,
            "len": 20,
            "col": [
                [255, 160, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            "fx": 0,
            "sx": 127,
            "ix": 127,
            "pal": 0,
            "sel": True,
            "rev": False,
            "cln": -1
        }
    ]
  },
  "info": {
    "ver": "0.8.4",
    "vid": 1903252,
    "leds": {
      "count": 40,
      "rgbw": True,
      "pin": [2],
      "pwr": 0,
      "maxpwr": 65000,
      "maxseg": 1
    },
    "name": "WLED Light",
    "udpport": 21324,
    "live": False,
    "fxcount": 80,
    "palcount": 47,
    "arch": "esp8266",
    "core": "2_4_2",
    "freeheap": 13264,
    "uptime": 17985,
    "opt": 127,
    "brand": "WLED",
    "product": "DIY light",
    "btype": "src",
    "mac": "60019423b441"
  }
}

class WledDevice:

    def __init__(self, ip, mdns_name):
        self.ip = ip
        self.name = mdns_name.split(".")[0]
        self.url = 'http://' + self.ip
        self.ledCount = 0
        self.mac = None
        self.segmentCount = 1  # Default number of segments in WLED
        self.segments = []
        self.getInitialState()

    def getInitialState(self):
        self.state = self.getLightState()
        self.getSegments()
        self.getLedCount()
        self.getMacAddr()

    def getLedCount(self):
        self.ledCount = self.state['info']['leds']['count']

    def getMacAddr(self):
        self.mac = ':'.join(self.state[
                            'info']['mac'][i:i+2] for i in range(0, 12, 2))

    def getSegments(self):
        self.segments = self.state['state']['seg']
        self.segmentCount = len(self.segments)

    def getLightState(self):
        data = wled
        return data

    def getSegState(self, seg):
        state = {}
        data = self.getLightState()['state']
        seg = data['seg'][seg]
        state['bri'] = seg['bri']
        state['on'] = data['on'] # Get on/off at light level
        state['bri'] = seg['bri']
        # Weird division by zero when a color is 0
        r = int(seg['col'][0][0])+1
        g = int(seg['col'][0][1])+1
        b = int(seg['col'][0][2])+1
        state['xy'] = self.convert_rgb_xy(r, g, b)
        state["colormode"] = "xy"
        return state
    
    def convert_rgb_xy(red, green, blue):
        red = pow((red + 0.055) / (1.0 + 0.055), 2.4) if red > 0.04045 else red / 12.92
        green = pow((green + 0.055) / (1.0 + 0.055), 2.4) if green > 0.04045 else green / 12.92
        blue = pow((blue + 0.055) / (1.0 + 0.055), 2.4) if blue > 0.04045 else blue / 12.92

    #Convert the RGB values to XYZ using the Wide RGB D65 conversion formula The formulas used:
        X = red * 0.664511 + green * 0.154324 + blue * 0.162028
        Y = red * 0.283881 + green * 0.668433 + blue * 0.047685
        Z = red * 0.000088 + green * 0.072310 + blue * 0.986039

    #Calculate the xy values from the XYZ values
        div = X + Y + Z
        if div < 0.000001:
            # set values to zero in case of div by zero
            x = 0
            y = 0
        else:
            x = X / div
            y = Y / div
        return [x, y]

print(WledDevice("192.168.1.0", "WLED Light.test").segments)

wledLights = {
    "192.168.1.0": {
        "seg" : [
            {
                "ledCount" : 10,
                "start" : 0,
            },
            {
                "ledCount" : 10,
                "start" : 10,
            }
        ]
    }
}

wledLights["192.168.1.0"]["seg"][0]["color"] = [r, g, b] #wledLights[light.protocol_cfg["ip"]]["color"] = [r, g, b]
wledLights["192.168.1.0"]["seg"][1]["color"] = [r, g, b] #wledLights[light.protocol_cfg["ip"]]["color"] = [r, g, b]

wled_udpmode = 4 #DNRGB mode
wled_secstowait = 2
for ip in wledLights.keys():
    for segments in wledLights[ip]["seg"]:
        udphead = bytes([wled_udpmode, wled_secstowait])
        start_seg = segments["start"].to_bytes(2,"big")
        color = bytes(segments["color"] * int(segments["ledCount"]))
        udpdata = udphead+start_seg+color
        #print(udpdata)