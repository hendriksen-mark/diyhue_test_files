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
        if all(x in capabilities for x in [f"{BASE_TYPE}on_off", f"{BASE_TYPE}segment_color_setting"]):
            handle_segmented_device(device, device_name, detectedLights)
        elif all(x in capabilities for x in [f"{BASE_TYPE}on_off", f"{BASE_TYPE}color_setting"]):
            handle_non_segmented_device(device, device_name, detectedLights)

def handle_segmented_device(device, device_name, detectedLights):
    for function in device["capabilities"]:
        if function["type"] == f"{BASE_TYPE}segment_color_setting":
            segments = len(function['parameters']['fields'][0]['options'])
        if function["type"] == f"{BASE_TYPE}range" and "brightness" in function["instance"]:
            bri_range = function['parameters']['range']
    logging.debug(f"Govee: Found {device_name} with {segments} segments")
    for option in range(segments):
        detectedLights.append({"protocol": "govee", "name": f"{device_name}-seg{option}", "modelid": "LLC010", "protocol_cfg": {"device_id": device["device"], "sku_model": device["sku"], "segmentedID": option, "bri_range": bri_range}})

def handle_non_segmented_device(device, device_name, detectedLights):
    for function in device["capabilities"]:
        if function["type"] == f"{BASE_TYPE}range" and "brightness" in function["instance"]:
            bri_range = function['parameters']['range']
    detectedLights.append({"protocol": "govee", "name": device_name, "modelid": "LLC010", "protocol_cfg": {"device_id": device["device"], "sku_model": device["sku"], "bri_range": bri_range}})
    logging.debug(f"Govee: Found {device_name}")

def set_light(light, data):
    logging.debug(f"Govee: <set_light> invoked! Device ID={light.name}")
    device_id = light.protocol_cfg["device_id"]
    model = light.protocol_cfg["sku_model"]
    request_data = {"sku": model, "device": device_id, "capability": {}}
    request_data["capability"] = []

    if "on" in data:
        request_data["capability"].append({
            "type": f"{BASE_TYPE}on_off",
            "instance": "powerSwitch",
            "value": data["on"]
        })

    if "bri" in data:
        request_data["capability"].append(create_brightness_capability(data['bri'], light.protocol_cfg.get("segmentedID", -1), light.protocol_cfg.get("bri_range", {})))

    if "xy" in data:
        r, g, b = convert_xy(data['xy'][0], data['xy'][1], data.get('bri', 255))
        request_data["capability"].append(create_color_capability(r, g, b, light.protocol_cfg.get("segmentedID", -1)))

    if "hue" in data or "sat" in data:
        hue = data.get('hue', 0)
        sat = data.get('sat', 0)
        bri = data.get('bri', 255)
        r, g, b = hsv_to_rgb(hue, sat, bri)
        request_data["capability"].append(create_color_capability(r, g, b, light.protocol_cfg.get("segmentedID", -1)))

    logging.debug({"requestId": "1", "payload": request_data})
    #response = requests.put(f"{BASE_URL}/device/control", headers=get_headers(), data=json.dumps({"requestId": "1", "payload": request_data}))
    #response.raise_for_status()

def create_brightness_capability(brightness, segment_id, bri_range):
    mapped_value = round(bri_range.get("min", 0) + ((brightness / 255) * (bri_range.get("max", 100) - bri_range.get("min", 0))),bri_range.get("precision", 0))
    if segment_id >= 0:
        return {
            "type": f"{BASE_TYPE}segment_color_setting",
            "instance": "segmentedBrightness",
            "value": {
                "segment": [segment_id],
                "brightness": mapped_value
            }
        }
    return {
        "type": f"{BASE_TYPE}range",
        "instance": "brightness",
        "value": mapped_value
    }

def create_color_capability(r, g, b, segment_id):
    if segment_id >= 0:
        return {
            "type": f"{BASE_TYPE}segment_color_setting",
            "instance": "segmentedColorRgb",
            "value": {
                "segment": [segment_id],
                "rgb": (((r & 0xFF) << 16) | ((g & 0xFF) << 8) | ((b & 0xFF) << 0))
            }
        }
    return {
        "type": f"{BASE_TYPE}color_setting",
        "instance": "colorRgb",
        "value": (((r & 0xFF) << 16) | ((g & 0xFF) << 8) | ((b & 0xFF) << 0))
    }

def get_light_state(light):
    logging.debug("Govee: <get_light_state> invoked!")
    device_id = light.protocol_cfg["device_id"]
    sku = light.protocol_cfg["sku_model"]
    response = requests.get(f"{BASE_URL}/device/state", headers=get_headers(), data=json.dumps({"requestId": "uuid", "payload": {"sku": sku, "device": device_id}}))
    response.raise_for_status()
    state_data = response.json().get("payload", {}).get("capabilities", {})
    state = {}
    for function in state_data:
        if function["type"] == f"{BASE_TYPE}online":
            state["reachable"] = function["state"]["value"] == "true"
        if function["type"] == f"{BASE_TYPE}on_off":
            state["on"] = function["state"]["value"] == 1
        if function["type"] == f"{BASE_TYPE}range" and "brightness" in function["instance"]:
            state["bri"] = round(((function["state"]["value"] / light.protocol_cfg["bri_range"]["max"]) * 255))
        if function["type"] == f"{BASE_TYPE}color_setting":
            rgb = function["state"]["value"]
            state["xy"] = convert_rgb_xy((rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF)
    return state
