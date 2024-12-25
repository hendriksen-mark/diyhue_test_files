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
    devices = govee.get("data", {})
    for device in devices:
        device_id = device["device"]
        device_name = device.get("deviceName", f'{device["sku"]}-{device_id.replace(":","")[10:]}')
        capabilities = [function["type"] for function in device["capabilities"]]
        model = get_model(capabilities)
        if model == "LST002":
            handle_segmented_device(device, device_name, detectedLights)
        else:
            detectedLights.append({"protocol": "govee", "name": device_name, "modelid": model, "protocol_cfg": {"device_id": device_id, "sku_model": device["sku"]}})
            logging.debug(f"Govee: Found {device_name} with model {model}")

def get_model(capabilities):
    if all(x in capabilities for x in [f"{BASE_TYPE}on_off", f"{BASE_TYPE}segment_color_setting"]):
        return "LST002"
    elif all(x in capabilities for x in [f"{BASE_TYPE}on_off", f"{BASE_TYPE}color_setting"]):
        return "LCT015"
    elif f"{BASE_TYPE}on_off" in capabilities:
        return "LOM010"
    return "Unknown"

def handle_segmented_device(device, device_name, detectedLights):
    for function in device["capabilities"]:
        if function["type"] == f"{BASE_TYPE}segment_color_setting":
            logging.debug(f"Govee: Found {device_name} with {len(function['parameters']['fields'][0]['options'])} segments")
            for option in function["parameters"]["fields"][0]["options"]:
                detectedLights.append({"protocol": "govee", "name": f"{device_name}-seg{option['value']}", "modelid": "LST002", "protocol_cfg": {"device_id": device["device"], "sku_model": device["sku"], "segmentedID": option["value"]}})

def set_light(light, data):
    logging.debug(f"Govee: <set_light> invoked! Device ID={light.protocol_cfg['device_id']}")
    device_id = light.protocol_cfg["device_id"]
    model = light.protocol_cfg["sku_model"]
    request_data = {"sku": model, "device": device_id, "capability": {}}

    if "bri" in data:
        request_data["capability"] = create_brightness_capability(data['bri'], light.protocol_cfg.get("segmentedID", 0))

    if "xy" in data:
        r, g, b = convert_xy(data['xy'][0], data['xy'][1], data.get('bri', 255))
        request_data["capability"] = create_color_capability(r, g, b, light.protocol_cfg.get("segmentedID", 0))

    if "ct" in data:
        request_data["capability"] = {"name": "colorTem", "value": data['ct']}

    if "hue" in data or "sat" in data:
        hue = data.get('hue', 0)
        sat = data.get('sat', 0)
        bri = data.get('bri', 255)
        r, g, b = hsv_to_rgb(hue, sat, bri)
        request_data["capability"] = create_color_capability(r, g, b, light.protocol_cfg.get("segmentedID", 0))

    response = requests.put(f"{BASE_URL}/device/control", headers=get_headers(), data=json.dumps({"requestId": "1", "payload": request_data}))
    response.raise_for_status()

def create_brightness_capability(brightness, segment_id):
    return {
        "type": f"{BASE_TYPE}segment_color_setting",
        "instance": "segmentedBrightness",
        "value": {
            "segment": [segment_id],
            "brightness": brightness
        }
    }

def create_color_capability(r, g, b, segment_id):
    return {
        "type": f"{BASE_TYPE}segment_color_setting",
        "instance": "segmentedColorRgb",
        "value": {
            "segment": [segment_id],
            "rgb": (((r & 0xFF) << 16) | ((g & 0xFF) << 8) | ((b & 0xFF) << 0))
        }
    }

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
