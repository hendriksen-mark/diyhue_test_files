state = {
    "object": 1,
    "lights": {
        1: {
            "on": False
        },
        2: {
            "on": False
        },
        3: {
            "on": False
        },
        4: {
            "on": False
        },
        5: {
            "on": False
        },
        6: {
            "on": False
        },
        7: {
            "on": False
        },
        8: {
            "on": False
        }
    }
}

def v1StateToV2(v1State):
    v2State = {}
    if "on" in v1State:
        v2State["on"] = {"on": v1State["on"]}
    if "bri" in v1State:
        v2State["dimming"] = {"brightness": round(v1State["bri"] / 2.54, 2)}
    if "ct" in v1State:
        v2State["color_temperature"] = {"mirek": v1State["ct"], "color_temperature_delta": {}}
    if "xy" in v1State:
        v2State["color"] = {
            "xy": {"x": v1State["xy"][0], "y": v1State["xy"][1]}}
    return v2State


for item in state["lights"]:
    light_state = state["lights"][item]
    v2State = v1StateToV2(light_state)
    print(v2State)