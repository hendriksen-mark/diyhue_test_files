import socket
import json
import logging
from typing import Dict, Any

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Define constants for ports
PORT_SCAN = 4001
PORT_RESPONSE = 4002
PORT_DEVSTATUS = 4003

# Define the expected incoming data
EXPECTED_DATA: Dict[int, Dict[str, Any]] = {
    PORT_SCAN: {
        "msg": {
            "cmd": "scan",
            "data": {
                "account_topic": "reserve"
            }
        }
    },
    PORT_DEVSTATUS: {
        "msg": {
            "cmd": "devStatus",
            "data": {}
        }
    }
}

def get_lan_ip() -> str:
    """
    Get the LAN IP address of the current machine.
    
    Returns:
        str: The LAN IP address.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

# Define the response data
RESPONSE_DATA: Dict[int, Dict[str, Any]] = {
    PORT_SCAN: {
        "msg": {
            "cmd": "scan",
            "data": {
                "ip": get_lan_ip(),
                "device": "1F:80:C5:32:32:36:72:4E",
                "sku": "Hxxxx",
                "bleVersionHard": "3.01.01",
                "bleVersionSoft": "1.03.01",
                "wifiVersionHard": "1.00.10",
                "wifiVersionSoft": "1.02.03"
            }
        }
    },
    PORT_DEVSTATUS: {
        "msg": {
            "cmd": "devStatus",
            "data": {
                "onOff": 1,
                "brightness": 100,
                "color": {
                    "r": 255,
                    "g": 0,
                    "b": 0
                },
                "colorTemInKelvin": 7200
            }
        }
    }
}

def start_receiver() -> None:
    """
    Start the receiver to listen for incoming data on specified ports.
    """
    try:
        # Create sockets to listen for incoming data on ports 4001 and 4003
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver_socket_4001, \
             socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver_socket_4003:
            
            receiver_socket_4001.bind(('0.0.0.0', PORT_SCAN))
            receiver_socket_4003.bind(('0.0.0.0', PORT_DEVSTATUS))
            
            logger.info("Listening on ports 4001 and 4003...")

            while True:
                handle_incoming_data(receiver_socket_4001, PORT_SCAN)
                handle_incoming_data(receiver_socket_4003, PORT_DEVSTATUS)
    except KeyboardInterrupt:
        logger.info("Receiver shutting down gracefully.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def handle_incoming_data(sock: socket.socket, port: int) -> None:
    """
    Handle incoming data on the specified socket and port.
    
    Args:
        sock (socket.socket): The socket to listen on.
        port (int): The port number.
    """
    try:
        data, addr = sock.recvfrom(1024)
        received_data = json.loads(data.decode())
        logger.info(f"Received data on port {port} from {addr}: {received_data}")

        # Check if the received data matches the expected data
        if received_data == EXPECTED_DATA[port]:
            logger.info(f"Received expected data on port {port} from {addr}, sending response...")
            send_response(addr[0], RESPONSE_DATA[port], PORT_RESPONSE)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON data on port {port}: {e}")
    except KeyError as e:
        logger.error(f"Unexpected data format on port {port}: {e}")
    except Exception as e:
        logger.error(f"Failed to process data on port {port}: {e}")

def send_response(ip: str, response_data: Dict[str, Any], port: int) -> None:
    """
    Send a response to the specified IP and port.
    
    Args:
        ip (str): The IP address to send the response to.
        response_data (Dict[str, Any]): The response data to send.
        port (int): The port number to send the response to.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender_socket:
            sender_socket.sendto(json.dumps(response_data).encode(), (ip, port))
            msg_type = response_data.get("msg", {}).get("cmd", "unknown")
            logger.info(f"Response of type '{msg_type}' sent to {ip} on port {port}")
    except Exception as e:
        logger.error(f"Failed to send response to {ip} on port {port}: {e}")

if __name__ == "__main__":
    start_receiver()
