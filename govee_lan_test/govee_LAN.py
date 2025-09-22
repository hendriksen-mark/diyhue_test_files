import socket
import json
import struct
import os
import yaml
import logging
from typing import Dict, List, Tuple, Generator
from time import sleep
import base64
import random

debug = True
#debug = False
#{
#    "terminate": "uwABsQAL",
#    "allowdata": "uwABsQEK"
#}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if debug else logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

IP_RANGE_START, IP_RANGE_END = 0, 255
SUB_IP_RANGE_START, SUB_IP_RANGE_END = 1, 1
MULTICAST_GROUP = '239.255.255.250'
DISCOVER_PORT, RECEIVE_PORT, CMD_PORT = 4001, 4002, 4003
DISCOVER_MESSAGE = {"msg": {"cmd": "scan", "data": {"account_topic": "reserve"}}}
DEV_MESSAGE = {"msg": {"cmd": "devStatus", "data": {}}}
STATUS_MESSAGE = {"msg": {"cmd": "status", "data": {}}}
BRI_MESSAGE = {"msg": {"cmd": "brightness", "data": {"value": 0}}}
ON_OFF_MESSAGE = {"msg": {"cmd": "turn", "data": {"value": 0}}}
COLOR_MESSAGE = {"msg": {"cmd": "colorwc", "data": {"color": {"r": 0, "g": 0, "b": 0}}}}
UDP_MESSAGE = {"msg": {"cmd": "razer", "data": {"pt": ""}}}
SEG_MESSAGE = {"msg": {"cmd": "ptReal", "data": {"command": ""}}}
SCAN_RESULTS_FILEPATH = os.path.join(os.path.dirname(__file__), 'scan_results.yaml')
CLEAR_MSG = 'Cleared file:'
RECEIVED_MSG = 'Received'
SAVING_MSG = 'Saving data to file:'
TIMEOUT_MSG = 'Timed out, no more responses'
FAILED_STATUS_MSG = 'Failed to get status from'

def get_lan_ip() -> str:
    """
    Get the LAN IP address of the current machine.
    
    Returns:
        str: The LAN IP address.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

def generate_ips(port: int) -> Generator[Tuple[str, int], None, None]:
    """
    Generate IP addresses within the specified range.
    
    Args:
        port (int): The port number to use.
    
    Yields:
        Generator[Tuple[str, int], None, None]: A generator yielding IP addresses and port tuples.
    """
    host_ip = get_lan_ip()
    logger.debug(f'Host IP: {host_ip}')
    host = host_ip.split('.')
    for sub_addr in range(SUB_IP_RANGE_START, SUB_IP_RANGE_END + 1):
        host[2] = str(sub_addr)
        for addr in range(IP_RANGE_START, IP_RANGE_END + 1):
            host[3] = str(addr)
            if (test_host := '.'.join(host)) != host_ip:
                yield (test_host, port)

def find_hosts(port: int = DISCOVER_PORT) -> List[str]:
    """
    Find hosts on the specified port.
    
    Args:
        port (int): The port number to scan.
    
    Returns:
        List[str]: A list of found hosts.
    """
    logger.debug(f'Scanning for hosts on port {port}')
    return [f'{host}:{port}' for host, port in generate_ips(port) if scan(host, port, 0.02) == 0]

def update_yaml_file(filepath: str, ip: str, data: Dict) -> None:
    """
    Update the YAML file with the provided data.
    
    Args:
        filepath (str): The path to the YAML file.
        ip (str): The IP address.
        data (dict): The data to update.
    """
    entry = {ip: data}
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r+') as file:
                file_data = yaml.safe_load(file) or {}
                file_data[ip] = {**file_data.get(ip, {}), **entry[ip]}
                file.seek(0)
                yaml.dump(file_data, file, default_flow_style=False)
        else:
            with open(filepath, 'w') as file:
                yaml.dump(entry, file, default_flow_style=False)
        logger.debug(f'Data saved to {filepath}')
    except (OSError, yaml.YAMLError) as e:
        logger.error(f'Failed to update YAML file {filepath}: {e}')

def manage_scan_results_file(ip: str = None, data: Dict = None, clear: bool = False) -> None:
    """
    Manage the scan results file.
    
    Args:
        ip (str, optional): The IP address. Defaults to None.
        data (dict, optional): The data to save. Defaults to None.
        clear (bool, optional): Whether to clear the file. Defaults to False.
    """
    try:
        if clear:
            clear_file(SCAN_RESULTS_FILEPATH)
        else:
            save_scan_results(ip, data)
    except Exception as e:
        logger.error(f'Failed to manage scan results file: {e}')

def save_scan_results(ip: str, data: Dict) -> None:
    """
    Save scan results to the file.
    
    Args:
        ip (str): The IP address.
        data (dict): The data to save.
    """
    logger.info(f'{RECEIVED_MSG} {data["msg"]["cmd"]} from {ip}')
    logger.debug(f'{SAVING_MSG} {data["msg"]["data"]}')
    update_yaml_file(SCAN_RESULTS_FILEPATH, ip, data["msg"]["data"])

def clear_file(filepath: str) -> None:
    """
    Clear the contents of a file.
    
    Args:
        filepath (str): The path to the file to clear.
    """
    try:
        with open(filepath, 'w') as file:
            file.write('')
        logger.debug(f'{CLEAR_MSG} {filepath}')
    except OSError as e:
        logger.error(f'Failed to clear file {filepath}: {e}')

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
        logger.info(f'Discover devices using multicast on ip {ip}')
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
    try:
        logger.debug(f'Sending message to ip {ip} and port {port}')
        sock.sendto(json.dumps(message).encode(), (ip, port))
        responses_received = receive_responses(sock, ip, is_multicast)
    except (socket.error, json.JSONDecodeError) as e:
        logger.error(f'Failed to send or receive message: {e}')
    finally:
        sock.close()
    return responses_received

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
            logger.debug(f'Waiting for response from {ip}')
            data, server = sock.recvfrom(1024)
            manage_scan_results_file(server[0] if is_multicast else ip, json.loads(data.decode()))
            responses_received = True
            if not is_multicast:
                return True
        except socket.timeout:
            if is_multicast:
                logger.warning(TIMEOUT_MSG)
            else:
                logger.debug(f'No more responses from {ip}')
            break
        except json.JSONDecodeError as e:
            logger.error(f'Failed to decode JSON response: {e}')
    return responses_received

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

def request_device_status(timeout: int = 5) -> None:
    """
    Request the device status from all scanned devices.
    
    Args:
        timeout (int): The timeout for the socket operations.
    """
    scan_results = load_scan_results()
    if not scan_results:
        return

    for ip in scan_results.keys():
        try:
            logger.info(f'Sending devStatus request to {ip} on port {CMD_PORT}')
            sock = create_socket(timeout)
            send_and_receive(sock, DEV_MESSAGE, ip, CMD_PORT)
        except (socket.timeout, socket.error) as e:
            logger.error(f'{FAILED_STATUS_MSG} {ip}: {e}')
        finally:
            sock.close()

def request_status(timeout: int = 5) -> None:
    """
    Request the device status from all scanned devices.
    
    Args:
        timeout (int): The timeout for the socket operations.
    """
    scan_results = load_scan_results()
    if not scan_results:
        return

    for ip in scan_results.keys():
        try:
            logger.info(f'Sending devStatus request to {ip} on port {CMD_PORT}')
            sock = create_socket(timeout)
            send_and_receive(sock, STATUS_MESSAGE, ip, CMD_PORT)
        except (socket.timeout, socket.error) as e:
            logger.error(f'{FAILED_STATUS_MSG} {ip}: {e}')
        finally:
            sock.close()

def set_light_color(timeout: int = 5, r: int = 0, g: int = 0, b: int = 0) -> None:
    """
    Set the color of the light.
    
    Args:
        timeout (int): The timeout for the socket operations.
        r (int): Red color value (0-255).
        g (int): Green color value (0-255).
        b (int): Blue color value (0-255).
    """
    logger.info(f'Setting light color to RGB({r}, {g}, {b})...')
    scan_results = load_scan_results()
    if not scan_results:
        return

    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        logger.error('RGB values must be between 0 and 255')
        return

    COLOR_MESSAGE["msg"]["data"]["color"] = {"r": r, "g": g, "b": b}

    for ip in scan_results.keys():
        try:
            logger.info(f'Sending color request to {ip} on port {CMD_PORT}')
            sock = create_socket(timeout)
            send_and_receive(sock, COLOR_MESSAGE, ip, CMD_PORT)
        except (socket.timeout, socket.error) as e:
            logger.error(f'{FAILED_STATUS_MSG} {ip}: {e}')
        finally:
            sock.close()

def set_light_on_off(timeout: int = 5, state: bool = True) -> None:
    """
    Set the on/off state of the light.
    
    Args:
        timeout (int): The timeout for the socket operations.
        state (bool): The state to set the light (True for on, False for off).
    """
    logger.info(f'Setting light on/off state to {"on" if state else "off"}...')
    scan_results = load_scan_results()
    if not scan_results:
        return

    if state not in [True, False]:
        logger.error('State must be True (on) or False (off)')
        return

    ON_OFF_MESSAGE["msg"]["data"]["value"] = 1 if state else 0

    for ip in scan_results.keys():
        try:
            logger.info(f'Sending on/off request to {ip} on port {CMD_PORT}')
            sock = create_socket(timeout)
            send_and_receive(sock, ON_OFF_MESSAGE, ip, CMD_PORT)
        except (socket.timeout, socket.error) as e:
            logger.error(f'{FAILED_STATUS_MSG} {ip}: {e}')
        finally:
            sock.close()

def set_light_brightness(timeout: int = 5, bri: int = 0) -> None:
    """
    Set the brightness of the light.
    
    Args:
        timeout (int): The timeout for the socket operations.
        bri (int): The brightness level to set (0-100).
    """
    logger.info(f'Setting light brightness to {bri}...')
    scan_results = load_scan_results()
    if not scan_results:
        return

    if not (0 <= bri <= 100):
        logger.error('Brightness value must be between 0 and 100')
        return

    BRI_MESSAGE["msg"]["data"]["value"] = bri

    for ip in scan_results.keys():
        try:
            logger.info(f'Sending brightness request to {ip} on port {CMD_PORT}')
            sock = create_socket(timeout)
            send_and_receive(sock, BRI_MESSAGE, ip, CMD_PORT)
        except (socket.timeout, socket.error) as e:
            logger.error(f'{FAILED_STATUS_MSG} {ip}: {e}')
        finally:
            sock.close()

def set_light_segment() -> None:
    """
    Set the segment of the light.
    
    Args:
        timeout (int): The timeout for the socket operations.
        seg (list): The segments to set.
    """
    logger.info(f'Setting light...')
    scan_results = load_scan_results()
    if not scan_results:
        return

    for ip in scan_results.keys():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.01)
        gradientFlag = 1
        points = 10
        header = [187, 0, 32, 176]
        rgb_values = []
        for _ in range(points):
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            rgb_values.extend([r, g, b])
        UDP_MESSAGE = []
        UDP_MESSAGE["msg"]["data"]["pt"] = "uwABsQEK"
        UDP_MESSAGE.append(UDP_MESSAGE.copy())
        byteArray = header + [gradientFlag, points] + rgb_values
        checksum = 0
        for byte in byteArray:
            checksum ^= byte
        byteArray.append(checksum)
        finalSendValue = (base64.b64encode(bytes(byteArray)).decode())
        UDP_MESSAGE["msg"]["data"]["pt"] = finalSendValue
        UDP_MESSAGE.append(UDP_MESSAGE.copy())
        for i in range(len(UDP_MESSAGE)):
            try:
                logger.info(f'{i} Sending segment request to {ip} on port {CMD_PORT}')
                sock.sendto(json.dumps(UDP_MESSAGE[i]).encode(), (ip, CMD_PORT))
                data, server = sock.recvfrom(1024)
                logger.debug(f"response: {json.loads(data.decode())}")
            except socket.timeout:
                x=1
                #logger.warning(f'Timed out, no more responses from {ip}')
            except Exception as e:
                logger.error(f'Error occurred: {e}')

def load_scan_results() -> Dict:
    """
    Load scan results from the YAML file if it exists.
    
    Returns:
        Dict: The scan results data or an empty dictionary if the file doesn't exist.
    """
    if not os.path.exists(SCAN_RESULTS_FILEPATH):
        logger.warning(f'No scan results file found at {SCAN_RESULTS_FILEPATH}')
        return {}
    with open(SCAN_RESULTS_FILEPATH, 'r') as file:
        return yaml.safe_load(file) or {}

def scan_for_lights() -> None:
    logger.info('Starting Govee LAN scan...')
    manage_scan_results_file(clear=True)
    if scan() != 0:
        logger.warning('No devices found using multicast, scanning using unicast...')
        find_hosts()

def main():
    """
    Main function to execute the script.
    """
    scan_for_lights()
    request_device_status()
    request_status()
    #set_light_brightness(bri=100)
    #set_light_color(r=255, g=100, b=0)  # Set light color to red
    #set_light_on_off(state=True)
    #set_light_segment()
    #set_light_on_off(state=False)
    #for i in range(20):
    #    request_device_status()
    #    sleep(10)
    #set_light_on_off(state=False)
    #request_device_status()

if __name__ == "__main__":
    main()
