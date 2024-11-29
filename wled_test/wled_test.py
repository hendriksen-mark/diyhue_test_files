import WledDevice

r = 255
g = 127
b = 9

print(WledDevice.WledDevice("192.168.1.0", "WLED Light.test").segments[2]["start"])

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