import socket
import json
import struct
import os
import yaml
import logging
from typing import Dict, List, Tuple, Generator

#debug = True
debug = False

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
CMD_MESSAGE = {"msg": {"cmd": "devStatus", "data": {}}}
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

def send_and_receive(sock: socket.socket, message: Dict, ip: str, port: int, is_multicast: bool) -> bool:
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
            data, server = sock.recvfrom(1024)
            manage_scan_results_file(server[0] if is_multicast else ip, json.loads(data.decode()))
            responses_received = True
            if not is_multicast:
                return True
        except socket.timeout:
            if is_multicast:
                logger.warning(TIMEOUT_MSG)
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
    if not os.path.exists(SCAN_RESULTS_FILEPATH):
        logger.warning(f'No scan results file found at {SCAN_RESULTS_FILEPATH}')
        return

    with open(SCAN_RESULTS_FILEPATH, 'r') as file:
        scan_results = yaml.safe_load(file) or {}

    for ip in scan_results.keys():
        try:
            logger.info(f'Sending devStatus request to {ip} on port {CMD_PORT}')
            sock = create_socket(timeout)
            send_and_receive(sock, CMD_MESSAGE, ip, CMD_PORT, False)
        except (socket.timeout, socket.error) as e:
            logger.error(f'{FAILED_STATUS_MSG} {ip}: {e}')
        finally:
            sock.close()

if __name__ == "__main__":
    manage_scan_results_file(clear=True)
    if scan() != 0:
        logger.warning('No devices found using multicast, scanning using unicast...')
        find_hosts()
    request_device_status()
