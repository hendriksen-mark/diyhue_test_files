import socket
import base64
import json
import time

device_ip = "192.168.1.94"  # ← vervang door IP van je Govee strip

# Gekende segment layout voor H619A = 20 segmenten van 6 leds
segment_count = 20
segment_size = 6

# Regenboogkleuren (20)
gradient_colors = [
    "ff0000", "ff7f00", "ffff00", "7fff00", "00ff00",
    "00ff7f", "00ffff", "007fff", "0000ff", "7f00ff",
    "ff00ff", "ff007f", "ff0000", "ff7f00", "ffff00",
    "7fff00", "00ff00", "00ff7f", "00ffff", "007fff"
]

# Start het commando met modedata
cmd = "010309000000000014"  # 01=begin, 03=custom mode, 14=20 segmenten hex

pixel_index = 0
for color, _ in zip(gradient_colors, range(segment_count)):
    cmd += f"{segment_size:02x}" + color
    for _ in range(segment_size):
        cmd += f"{pixel_index:02x}"
        pixel_index += 1

# Splits in 17-byte (34 hex-char) delen
chunks = [cmd[i:i + 34] for i in range(0, len(cmd), 34)]

packets = []
for idx, chunk in enumerate(chunks):
    header = "a3" + (f"{idx:02x}" if idx < len(chunks) - 1 else "ff")
    full_packet = header + chunk
    full_packet = full_packet.ljust(38, "0")  # opvullen
    checksum = 0
    for i in range(0, len(full_packet), 2):
        checksum ^= int(full_packet[i:i + 2], 16)
    full_packet += f"{checksum:02x}"
    packets.append(base64.b64encode(bytes.fromhex(full_packet)).decode())

# Voeg sluitpakket toe
packets.append("MwUKIAMAAAAAAAAAAAAAAAAAAB8=")

# JSON
msg = {
    "msg": {
        "cmd": "ptReal",
        "data": {
            "command": packets
        }
    }
}

msg = {
    "msg": {
        "cmd": "colorwc",
        "data": {
            "r": 255, "g": 0, "b": 0
        }
    }
}

msg = {"msg": {"cmd": "brightness", "data": {"value": 100}}}

# Verstuur
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for pkt in [json.dumps(msg).encode()]:
    sock.sendto(pkt, (device_ip, 4003))
    time.sleep(0.05)
