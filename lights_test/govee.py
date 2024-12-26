import json
import requests
import logManager
from colors import convert_rgb_xy, convert_xy, hsv_to_rgb
from govee_data import govee, return_state_govee

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
        device_id = device["device"]
        device_name = device.get("deviceName", f'{device["sku"]}-{device_id.replace(":","")[10:]}')
        capabilities = [function["type"] for function in device["capabilities"]]
        if has_capabilities(capabilities, ["on_off", "segment_color_setting"]):
            handle_segmented_device(device, device_name, detectedLights)
        elif has_capabilities(capabilities, ["on_off", "color_setting"]):
            handle_non_segmented_device(device, device_name, detectedLights)

def has_capabilities(capabilities, required_capabilities):
    return all(f"{BASE_TYPE}{cap}" in capabilities for cap in required_capabilities)

def handle_segmented_device(device, device_name, detectedLights):
    segments, bri_range = get_segmented_device_info(device)
    logging.debug(f"Govee: Found {device_name} with {segments} segments")
    for option in range(segments):
        detectedLights.append(create_light_entry(device, device_name, option, bri_range))

def get_segmented_device_info(device):
    segments = 0
    bri_range = {}
    for function in device["capabilities"]:
        if function["type"] == f"{BASE_TYPE}segment_color_setting":
            segments = len(function['parameters']['fields'][0]['options'])
        if function["type"] == f"{BASE_TYPE}range" and "brightness" in function["instance"]:
            bri_range = function['parameters']['range']
    return segments, bri_range

def create_light_entry(device, device_name, segment_id, bri_range):
    return {
        "protocol": "govee",
        "name": f"{device_name}-seg{segment_id}" if segment_id >= 0 else device_name,
        "modelid": "LLC010",
        "protocol_cfg": {
            "device_id": device["device"],
            "sku_model": device["sku"],
            "segmentedID": segment_id,
            "bri_range": bri_range
        }
    }

def handle_non_segmented_device(device, device_name, detectedLights):
    bri_range = get_brightness_range(device)
    detectedLights.append(create_light_entry(device, device_name, -1, bri_range))
    logging.debug(f"Govee: Found {device_name}")

def get_brightness_range(device):
    for function in device["capabilities"]:
        if function["type"] == f"{BASE_TYPE}range" and "brightness" in function["instance"]:
            return function['parameters']['range']
    return {}

def set_light(light, data):
    logging.debug(f"Govee: <set_light> invoked! Device ID={light.name}")
    for date_type in data:
        request_data = create_request_data(light, data, date_type)
        if request_data is not None:
            logging.debug({"requestId": "1", "payload": request_data})
            #response = requests.put(f"{BASE_URL}/device/control", headers=get_headers(), data=json.dumps({"requestId": "1", "payload": request_data}))
            #response.raise_for_status()

def create_request_data(light, data, data_type):
    device_id = light.protocol_cfg["device_id"]
    model = light.protocol_cfg["sku_model"]
    request_data = {"sku": model, "device": device_id}

    if data_type == "on":
        request_data["capability"] = create_on_off_capability(data["on"])
        return request_data

    elif data_type == "bri":
        request_data["capability"] = create_brightness_capability(data['bri'], light.protocol_cfg.get("segmentedID", -1), light.protocol_cfg.get("bri_range", {}))
        return request_data

    elif data_type == "xy":
        r, g, b = convert_xy(data['xy'][0], data['xy'][1], data.get('bri', 255))
        request_data["capability"] = create_color_capability(r, g, b, light.protocol_cfg.get("segmentedID", -1))
        return request_data

    elif data_type == "hue" or data_type == "sat":
        hue = data.get('hue', 0)
        sat = data.get('sat', 0)
        bri = data.get('bri', 255)
        r, g, b = hsv_to_rgb(hue, sat, bri)
        request_data["capability"] = create_color_capability(r, g, b, light.protocol_cfg.get("segmentedID", -1))
        return request_data

    else:
        return None

def create_on_off_capability(value):
    return {
        "type": f"{BASE_TYPE}on_off",
        "instance": "powerSwitch",
        "value": value
    }

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
    #response = requests.get(f"{BASE_URL}/device/state", headers=get_headers(), data=json.dumps({"requestId": "uuid", "payload": {"sku": light.protocol_cfg["sku_model"], "device": light.protocol_cfg["device_id"]}}))
    #response.raise_for_status()
    #return parse_light_state(response.json().get("payload", {}).get("capabilities", {}), light)
    return parse_light_state(return_state_govee.get("payload", {}).get("capabilities", {}), light)

def parse_light_state(state_data, light):
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
