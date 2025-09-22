import json
import logManager
from functions.colors import convert_rgb_xy, convert_xy, hsv_to_rgb
from typing import List, Dict, Any, Generator, Tuple
import socket
import struct

logging = logManager.logger.get_logger(__name__)

MULTICAST_GROUP = '239.255.255.250'
DISCOVER_PORT, RECEIVE_PORT, CMD_PORT = 4001, 4002, 4003
DISCOVER_MESSAGE = {"msg": {"cmd": "scan", "data": {"account_topic": "reserve"}}}
DEV_MESSAGE = {"msg": {"cmd": "devStatus", "data": {}}}
CMD_MESSAGE = {"msg": {"cmd": "status", "data": {}}}
BRI_MESSAGE = {"msg": {"cmd": "brightness", "data": {"value": 0}}}
ON_OFF_MESSAGE = {"msg": {"cmd": "turn", "data": {"value": 0}}}
COLOR_MESSAGE = {"msg": {"cmd": "colorwc", "data": {"color": {"r": 0, "g": 0, "b": 0}}}}
TIMEOUT_MSG = 'Timed out, no more responses'
FAILED_STATUS_MSG = 'Failed to get status from'

responded_devices = []

def is_json(content: str) -> bool:
    """
    Check if the content is valid JSON.

    Args:
        content (str): The content to check.

    Returns:
        bool: True if the content is valid JSON, False otherwise.
    """
    logging.debug(f"Checking if content is valid JSON: {content}")
    try:
        json.loads(content)
    except ValueError:
        return False
    return True

def save_scan_results(ip: str, data: Dict) -> None:
    """
    Save scan results to the file.
    
    Args:
        ip (str): The IP address.
        data (dict): The data to save.
    """
    responded_devices.append({ip: data["msg"]["data"]})

def receive_responses(sock: socket.socket, ip: str, is_multicast: bool) -> bool:
    """
    Receive responses from the socket.
    
    Args:
        sock (socket.socket): The socket to use.
        ip (str): The IP address to send to.
        is_multicast (bool): Whether the message is multicast.
    
    Returns:
        bool: Whether responses were received.
    """
    responses_received = False
    while True:
        try:
            data, server = sock.recvfrom(1024)
            save_scan_results(server[0] if is_multicast else ip, json.loads(data.decode()))
            responses_received = True
            if not is_multicast:
                return True
        except socket.timeout:
            if is_multicast:
                logging.warning(TIMEOUT_MSG)
            else:
                logging.debug(f'No more responses from {ip}')
            break
        except json.JSONDecodeError as e:
            logging.error(f'Failed to decode JSON response: {e}')
    return responses_received

def send_and_receive(sock: socket.socket, message: Dict, ip: str, port: int, is_multicast: bool = False) -> bool:
    """
    Send a message and receive responses.
    
    Args:
        sock (socket.socket): The socket to use.
        message (dict): The message to send.
        ip (str): The IP address to send to.
        port (int): The port number to send to.
        is_multicast (bool): Whether the message is multicast.
    
    Returns:
        bool: Whether responses were received.
    """
    responses_received = False
    if is_multicast:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
    try:
        sock.sendto(json.dumps(message).encode(), (ip, port))
        responses_received = receive_responses(sock, ip, is_multicast)
    except (socket.error, json.JSONDecodeError) as e:
        logging.error(f'Failed to send or receive message: {e}')
    finally:
        sock.close()
    return responses_received

def create_socket(timeout: int) -> socket.socket:
    """
    Create a socket with the specified timeout.
    
    Args:
        timeout (int): The timeout for the socket.
    
    Returns:
        socket.socket: The created socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    sock.bind(('0.0.0.0', RECEIVE_PORT))
    return sock

def scan(ip: str = MULTICAST_GROUP, port: int = DISCOVER_PORT, timeout: int = 5) -> int:
    """
    Scan for devices on the network.
    
    Args:
        ip (str, optional): The IP address to scan. Defaults to MULTICAST_GROUP.
        port (int, optional): The port number to scan. Defaults to DISCOVER_PORT.
        timeout (int, optional): The timeout for the scan. Defaults to 5.
    
    Returns:
        int: 0 if devices were found, 1 otherwise.
    """
    sock = create_socket(timeout)
    return 0 if send_and_receive(sock, DISCOVER_MESSAGE, ip, port, ip == MULTICAST_GROUP) else 1

def generate_ips(port: int) -> Generator[Tuple[str, int], None, None]:
    """
    Generate IP addresses within the specified range.
    
    Args:
        port (int): The port number to use.
    
    Yields:
        Generator[Tuple[str, int], None, None]: A generator yielding IP addresses and port tuples.
    """
    import configManager
    bridgeConfig = configManager.bridgeConfig.yaml_config
    rangeConfig = bridgeConfig["config"]["IP_RANGE"]
    HOST_IP = configManager.runtimeConfig.arg["HOST_IP"]
    ip_range_start = rangeConfig["IP_RANGE_START"]
    ip_range_end = rangeConfig["IP_RANGE_END"]
    sub_ip_range_start = rangeConfig["SUB_IP_RANGE_START"]
    sub_ip_range_end = rangeConfig["SUB_IP_RANGE_END"]
    host = HOST_IP.split('.')
    for sub_addr in range(sub_ip_range_start, sub_ip_range_end + 1):
        host[2] = str(sub_addr)
        for addr in range(ip_range_start, ip_range_end + 1):
            host[3] = str(addr)
            if (test_host := '.'.join(host)) != HOST_IP:
                yield (test_host, port)

def find_hosts(port: int = DISCOVER_PORT) -> List[str]:
    """
    Find hosts on the specified port.
    
    Args:
        port (int): The port number to scan.
    
    Returns:
        List[str]: A list of found hosts.
    """
    logging.debug(f'Scanning for hosts on port {port}')
    return [f'{host}:{port}' for host, port in generate_ips(port) if scan(host, port, 0.02) == 0]

def discover(detectedLights: List[Dict[str, Any]]) -> None:
    """
    Discover Govee lights and append them to the detectedLights list.

    Args:
        detectedLights (list): List to append discovered lights to.
    """
    global responded_devices
    responded_devices = []  # Reset the list
    logging.debug("Govee: <discover> invoked!")
    if scan() != 0:
        logging.warning('No devices found using multicast, scanning using unicast...')
        find_hosts()
    if not responded_devices:
        logging.warning('No devices found')
        return
    logging.debug(f"Govee: Found {len(responded_devices)} devices")
    for device in responded_devices:
        try:
            ip = list(device.keys())[0]
            data = device[ip]
            logging.debug(f"Govee: Found device {ip}: {data}")
            if data and is_json(json.dumps(data)):  # Convert data to JSON string
                detectedLights.append(create_light_entry(data))
            else:
                logging.error("Govee: Invalid response data")
        except (IndexError, KeyError) as e:
            logging.error(f"Govee: Error processing device data: {e}")

def create_light_entry(device: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a light entry for a Govee device.

    Args:
        device (Dict[str, Any]): The device information.

    Returns:
        Dict[str, Any]: The light entry.
    """
    return {
        "protocol": "govee",
        "name": device.get("deviceName", f'{device["sku"]}-{device["device"].replace(":","")[10:]}'),
        "modelid": "LCX002",
        "protocol_cfg": {
            "ip": device["ip"],
            "points_capable": 5,
            "device_id": device["device"],
            "sku_model": device["sku"],
            "bri_range": {
                "min": 1,
                "max": 100,
                "precision": 1
            }
        }
    }

def set_light(light: Any, data: Dict[str, Any]) -> None:
    """
    Set the state of a Govee light.

    Args:
        light (Any): The light object containing protocol configuration.
        data (dict): The data containing state information to set.
    """
    logging.debug(f"Govee: <set_light> invoked with {data}")
    for date_type in data:
        request_data = create_request_data(light, data, date_type)
        if request_data is not None:
            logging.debug(f"Govee: Setting {light.protocol_cfg['device_id']} with {json.dumps(request_data, indent=4)}")


def create_request_data(light: Any, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
    """
    Create the request data for setting the state of a Govee light.

    Args:
        light (Any): The light object containing protocol configuration.
        data (Dict[str, Any]): The data containing state information to set.
        data_type (str): The type of data to set.

    Returns:
        Dict[str, Any]: The request data.
    """
    request_data = {"msg": {}}

    if data_type == "on":
        request_data["msg"] = create_on_off_capability(data["on"])
        return request_data

    elif data_type == "bri":
        request_data["msg"] = create_brightness_capability(data['bri'], light.protocol_cfg.get("bri_range", {}))
        return request_data

    elif data_type == "xy":
        r, g, b = convert_xy(data['xy'][0], data['xy'][1], data.get('bri', 255))
        request_data["msg"] = create_color_capability(r, g, b)
        return request_data

    elif data_type == "hue" or data_type == "sat":
        hue = data.get('hue', 0)
        sat = data.get('sat', 0)
        bri = data.get('bri', 255)
        r, g, b = hsv_to_rgb(hue, sat, bri)
        request_data["msg"] = create_color_capability(r, g, b)
        return request_data

    else:
        return None

def create_on_off_capability(value: bool) -> Dict[str, Any]:
    """
    Create the on/off capability for a Govee light.

    Args:
        value (bool): The on/off value.

    Returns:
        Dict[str, Any]: The on/off capability.
    """
    return {
        "cmd": "turn",
        "data": {
            "value": 1 if value else 0
        },
    }

def create_brightness_capability(brightness: int, bri_range: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create the brightness capability for a Govee light.

    Args:
        brightness (int): The brightness value.
        bri_range (Dict[str, Any]): The brightness range.

    Returns:
        Dict[str, Any]: The brightness capability.
    """
    mapped_value = round(bri_range.get("min", 0) + ((brightness / 255) * (bri_range.get("max", 100) - bri_range.get("min", 0))),bri_range.get("precision", 0))
    return {
        "cmd": "brightness",
        "data": {
            "value": int(mapped_value)
        }
    }

def create_color_capability(r: int, g: int, b: int) -> Dict[str, Any]:
    """
    Create the color capability for a Govee light.

    Args:
        r (int): The red value.
        g (int): The green value.
        b (int): The blue value.
    Returns:
        Dict[str, Any]: The color capability.
    """
    return {
        "cmd": "colorwc",
        "data": {
            "color": {
                "r": r,
                "g": g,
                "b": b
            }
        }
    }

def get_light_state(light: Any) -> Dict[str, Any]:
    """
    Get the current state of a Govee light.

    Args:
        light (Any): The light object containing protocol configuration.

    Returns:
        dict: The current state of the light.
    """
    global responded_devices
    responded_devices = []  # Reset the list
    ip = light.protocol_cfg["ip"]
    timeout: int = 5
    try:
        sock = create_socket(timeout)
        response = send_and_receive(sock, CMD_MESSAGE, ip, CMD_PORT)
    except (socket.timeout, socket.error) as e:
        logging.error(f'{FAILED_STATUS_MSG} {ip}: {e}')
    finally:
        sock.close()
    if not response:
        logging.error(f'{FAILED_STATUS_MSG} {ip}')
        raise Exception("Failed to get status from device")
    state = {}
    for device in responded_devices:
        if ip in device:
            state['bri'] = device[ip]["brightness"]
            state["on"] = True if device[ip]["onOff"] else False
            break
    return state
