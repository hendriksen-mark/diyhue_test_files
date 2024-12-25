import json
import requests
import logManager
from colors import convert_rgb_xy, convert_xy, hsv_to_rgb, rgbBrightness
from govee_data import govee

logging = logManager.logger.get_logger(__name__)

API_KEY = ""
BASE_URL = "https://openapi.api.govee.com/router/api/v1/"
BASE_TYPE = "devices.capabilities."

def get_headers():
    return {
        "Govee-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

def discover(detectedLights):
    logging.debug("Govee: <discover> invoked!")
    #response = requests.get(f"{BASE_URL}/devices", headers=get_headers())
    #response.raise_for_status()
    #devices = govee.json().get("data", {})
    devices = govee.get("data", {})
    for device in devices:
        #logging.debug(device)
        device_id = device["device"]
        device_name = device.get("deviceName", f'{device["sku"]}-{device_id.replace(":","")[10:]}')
        capabilities = []
        for function in device["capabilities"]:
            capabilities.append(function["type"])
        if all(x in capabilities for x in [f"{BASE_TYPE}on_off", f"{BASE_TYPE}segment_color_setting"]):
            model = "LST002"
            for function in device["capabilities"]:
                if function["type"] == f"{BASE_TYPE}segment_color_setting":
                    logging.debug(f"Govee: Found {device_name} with {len(function['parameters']['fields'][0]['options'])} segments")
                    for option in function["parameters"]["fields"][0]["options"]:
                        detectedLights.append({"protocol": "govee", "name": f"{device_name}-seg{option['value']}", "modelid": model, "protocol_cfg": {"device_id": device_id, "sku_model": device["sku"], "segmentedID": option["value"]}})
            continue
        elif all(x in device["capabilities"] for x in [f"{BASE_TYPE}on_off", f"{BASE_TYPE}color_setting"]):
            model = "LCT015"
        elif all(x in device["capabilities"] for x in [f"{BASE_TYPE}on_off"]):
            model = "LOM010"
        detectedLights.append({"protocol": "govee", "name": device_name, "modelid": model, "protocol_cfg": {"device_id": device_id, "sku_model": device["sku"]}})
        logging.debug(f"Govee: Found {device_name} with model {model}")

def set_light(light, data):
    logging.debug(f"Govee: <set_light> invoked! Device ID={light.protocol_cfg['device_id']}")
    device_id = light.protocol_cfg["device_id"]
    model = light.protocol_cfg["sku_model"]
    request_data = {"sku": model, "device": device_id, "capability": {}}

    if "bri" in data:
        brightness = data['bri']
        request_data["capability"] = {
            "type": f"{BASE_TYPE}segment_color_setting",
            "instance": "segmentedBrightness",
            "value": {
                "segment": [light.protocol_cfg.get("segmentedID", 0)]},
                "brightness": brightness
        }

    if "xy" in data:
        r,g,b = convert_xy(data['xy'][0], data['xy'][1], data.get('bri', 255))
        request_data["capability"] = {
            "type": f"{BASE_TYPE}segment_color_setting",
            "instance": "segmentedColorRgb",
            "value": {
                "segment": [light.protocol_cfg.get("segmentedID", 0)]},
                "rgb": (((r & 0xFF) << 16) | ((g & 0xFF) << 8) | ((b & 0xFF) << 0))
        }

    if "ct" in data:
        request_data["capability"] = {"name": "colorTem", "value": data['ct']}

    if "hue" in data or "sat" in data:
        hue = data.get('hue', 0)
        sat = data.get('sat', 0)
        bri = data.get('bri', 255)
        r,g,b = hsv_to_rgb(hue, sat, bri)
        request_data["capability"] = {
            "type": f"{BASE_TYPE}segment_color_setting",
            "instance": "segmentedColorRgb",
            "value": {
                "segment": [light.protocol_cfg.get("segmentedID", 0)]},
                "rgb": (((r & 0xFF) << 16) | ((g & 0xFF) << 8) | ((b & 0xFF) << 0))
        }

    response = requests.put(f"{BASE_URL}/device/control", headers=get_headers(), data=json.dumps({"requestId": "1", "payload": request_data}))
    response.raise_for_status()

def get_light_state(light):
    logging.debug("Govee: <get_light_state> invoked!")
    device_id = light.protocol_cfg["device_id"]
    response = requests.get(f"{BASE_URL}/device/state?device={device_id}", headers=get_headers())
    response.raise_for_status()
    state_data = response.json().get("data", {}).get("properties", {})
    state = {"on": state_data.get("powerState", "off") == "on"}
    if "brightness" in state_data:
        state["bri"] = state_data["brightness"]
    if "color" in state_data:
        color = state_data["color"]
        state["xy"] = convert_rgb_xy(color["r"], color["g"], color["b"])
    if "colorTem" in state_data:
        state["ct"] = state_data["colorTem"]
    return state
