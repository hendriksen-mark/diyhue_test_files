import logManager
from light_types import lightTypes
from configHandler import bridgeConfig_Light
import Light
import socket
import json
import wled
import native_multi
import hue
import govee
from typing import Dict, List, Tuple, Union, Generator

logging = logManager.logger.get_logger(__name__)

scan_active = False

#discover.py
def nextFreeId() -> str:
    i = 1
    while (str(i)) in bridgeConfig_Light:
        i += 1
    return str(i)

def pretty_json(data: Union[Dict, List]) -> str:
    """
    Convert a dictionary or list to a pretty-printed JSON string.

    Args:
        data (Union[Dict, List]): The data to convert.

    Returns:
        str: The pretty-printed JSON string.
    """
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

def scanHost(host: str, port: int) -> int:
    """
    Scan a host to check if a port is open.

    Args:
        host (str): The host to scan.
        port (int): The port to check.

    Returns:
        int: The result of the connection attempt (0 if successful).
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Very short timeout. If scanning fails this could be increased
    sock.settimeout(0.02)
    result = sock.connect_ex((host, port))
    sock.close()
    return result

def iter_ips(port: int) -> Generator[Tuple[str, int], None, None]:
    """
    Generate IP addresses within the configured range.

    Args:
        port (int): The port to check.

    Yields:
        Generator[Tuple[str, int], None, None]: A tuple of host and port.
    """
    HOST_IP = "192.168.1.3"
    scan_on_host_ip = False
    ip_range_start = 0
    ip_range_end = 255
    sub_ip_range_start = 1
    sub_ip_range_end = 1
    host = HOST_IP.split('.')
    if scan_on_host_ip:
        yield ('127.0.0.1', port)
    for sub_addr in range(sub_ip_range_start, sub_ip_range_end + 1):
        host[2] = str(sub_addr)
        for addr in range(ip_range_start, ip_range_end + 1):
            host[3] = str(addr)
            test_host = '.'.join(host)
            if test_host != HOST_IP:
                yield (test_host, port)

def find_hosts(port: int) -> List[str]:
    """
    Find hosts with the specified port open.

    Args:
        port (int): The port to check.

    Returns:
        List[str]: A list of hosts with the port open.
    """
    return [f'{host}:{port}' for host, port in iter_ips(port) if scanHost(host, port) == 0]

def addNewLight(modelid: str, name: str, protocol: str, protocol_cfg: Dict) -> Union[str, bool]:
    """
    Add a new light to the bridge configuration.

    Args:
        modelid (str): The model ID of the light.
        name (str): The name of the light.
        protocol (str): The protocol used by the light.
        protocol_cfg (Dict): The protocol configuration.

    Returns:
        Union[int, bool]: The ID of the new light or False if the model ID is not found.
    """
    newLightID = nextFreeId()
    if modelid in lightTypes:
        light = lightTypes[modelid]
        light.update({
            "name": name,
            "id_v1": newLightID,
            "modelid": modelid,
            "protocol": protocol,
            "protocol_cfg": protocol_cfg
        })
        newObject = Light.Light(light)
        bridgeConfig_Light[newLightID] = newObject
        return newLightID
    return False

def get_device_ips() -> List[str]:
    """
    Get the IP addresses of devices to scan.

    Returns:
        List[str]: A list of device IP addresses.
    """
    if scan_active:
        return [host for ports in [80, 81] for host in find_hosts(ports)]
    return []

def update_light_ip(lightObj: Light.Light, light: Dict) -> None:
    """
    Update the IP address of a light.

    Args:
        lightObj (Light.Light): The light object to update.
        light (Dict): The new light data.
    """
    if "ip" in light["protocol_cfg"]:
        lightObj.protocol_cfg["ip"] = light["protocol_cfg"]["ip"]
    if light["protocol"] == "wled":
        lightObj.protocol_cfg.update({
            "ledCount": light["protocol_cfg"]["ledCount"],
            "segment_start": light["protocol_cfg"]["segment_start"],
            "udp_port": light["protocol_cfg"]["udp_port"]
        })
    if light["protocol"] == "govee":
        lightObj.protocol_cfg.update({
            "bri_range": light["protocol_cfg"]["bri_range"]
        })
    logging.info(f"Update IP/config for light {light['name']}")

def is_light_matching(lightObj: Light.Light, light: Dict) -> bool:
    """
    Check if a light matches an existing light object.

    Args:
        lightObj (Light.Light): The existing light object.
        light (Dict): The new light data.

    Returns:
        bool: True if the light matches, False otherwise.
    """
    protocol = light["protocol"]
    if protocol == "native_multi":
        return (lightObj.protocol_cfg["mac"] == light["protocol_cfg"]["mac"] and
                lightObj.protocol_cfg["light_nr"] == light["protocol_cfg"]["light_nr"] and
                lightObj.modelid == light["modelid"])
    if protocol in ["yeelight", "tasmota", "tradfri", "hyperion", "tpkasa"]:
        return lightObj.protocol_cfg["id"] == light["protocol_cfg"]["id"] and lightObj.modelid == light["modelid"]
    if protocol in ["shelly", "native", "native_single", "esphome", "elgato"]:
        return lightObj.protocol_cfg["mac"] == light["protocol_cfg"]["mac"] and lightObj.modelid == light["modelid"]
    if protocol in ["hue", "deconz"]:
        return lightObj.protocol_cfg["uniqueid"] == light["protocol_cfg"]["uniqueid"] and lightObj.modelid == light["modelid"]
    if protocol == "wled":
        return (lightObj.protocol_cfg["mac"] == light["protocol_cfg"]["mac"] and
                lightObj.protocol_cfg["segmentId"] == light["protocol_cfg"]["segmentId"] and
                lightObj.modelid == light["modelid"])
    if protocol == "homeassistant_ws":
        return lightObj.protocol_cfg["entity_id"] == light["protocol_cfg"]["entity_id"] and lightObj.modelid == light["modelid"]
    if protocol == "govee":
        return (lightObj.protocol_cfg["device_id"] == light["protocol_cfg"]["device_id"] and
                lightObj.protocol_cfg["sku_model"] == light["protocol_cfg"]["sku_model"] and
                lightObj.protocol_cfg.get("segmentedID", -1) == light["protocol_cfg"].get("segmentedID", -1))
    return False

def discover_lights(detectedLights: List[Dict], device_ips: List[str]) -> None:
    """
    Discover lights on the network.

    Args:
        detectedLights (List[Dict]): A list to store detected lights.
        device_ips (List[str]): A list of device IP addresses to scan.
    """
    #mqtt.discover(bridgeConfig["config"]["mqtt"])
    #deconz.discover(detectedLights, bridgeConfig["config"]["deconz"])
    #homeAssistantWS.discover(detectedLights)
    #yeelight.discover(detectedLights)
    native_multi.discover(detectedLights, device_ips)
    #tasmota.discover(detectedLights, device_ips)
    wled.discover(detectedLights, device_ips)
    hue.discover(detectedLights, hueUser="", ip="")
    #shelly.discover(detectedLights, device_ips)
    #esphome.discover(detectedLights, device_ips)
    #tradfri.discover(detectedLights, bridgeConfig["config"]["tradfri"])
    #hyperion.discover(detectedLights)
    #tpkasa.discover(detectedLights)
    #elgato_ips = find_hosts(9123)
    #logging.info(pretty_json(elgato_ips))
    #elgato.discover(detectedLights, elgato_ips)
    govee.discover(detectedLights)

def scanForLights() -> None:
    device_ips = get_device_ips()
    if device_ips:
        logging.info(f"Scanning for lights on\n{pretty_json(device_ips)}")
    detectedLights = []
    discover_lights(detectedLights, device_ips)

    for light in detectedLights:
        lightIsNew = True
        for key, lightObj in bridgeConfig_Light.items():
            if lightObj.protocol == light["protocol"] and is_light_matching(lightObj, light):
                update_light_ip(lightObj, light)
                lightIsNew = False
                break
        if lightIsNew:
            logging.info(f"Add new light {light['name']}")
            lightId = addNewLight(light["modelid"], light["name"], light["protocol"], light["protocol_cfg"])
            if lightId:
                logging.info(f"New light added with id {int(lightId)}")
            else:
                logging.info(f"Failed to add new light {light['name']}")
