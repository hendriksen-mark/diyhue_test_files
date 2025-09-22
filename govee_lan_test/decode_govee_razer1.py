import base64

HEADER_LENGTH = 4
GRADIENT_FLAG_LENGTH = 1
POINTS_LENGTH = 1
COLOR_COUNT = 10
COLOR_BYTES = COLOR_COUNT * 3

def calculate_checksum(data):
    """XOR all bytes in the array"""
    checksum = 0
    for byte in data:
        checksum ^= byte
    return checksum

def decode_colors(b64_string):
    """Decode base64 string into parts: header, gradientFlag, colors"""
    decoded_bytes = base64.b64decode(b64_string)
    print("Decoded bytes:", decoded_bytes)
    
    header = decoded_bytes[:HEADER_LENGTH]
    gradient_flag = decoded_bytes[HEADER_LENGTH]
    points = decoded_bytes[HEADER_LENGTH + 1]
    
    color_start = HEADER_LENGTH + GRADIENT_FLAG_LENGTH + POINTS_LENGTH
    color_bytes = decoded_bytes[color_start:color_start + COLOR_BYTES]
    checksum = decoded_bytes[color_start + COLOR_BYTES]

    colors = [
        (color_bytes[i], color_bytes[i+1], color_bytes[i+2])
        for i in range(0, len(color_bytes), 3)
    ]
    
    # Validate checksum
    computed_checksum = calculate_checksum(decoded_bytes[:-1])
    if checksum != computed_checksum:
        raise ValueError(f"Checksum mismatch! Expected {checksum}, calculated {computed_checksum}")

    return header, gradient_flag, points, colors

def encode_colors(header, gradient_flag, points, colors):
    """Encode parts into a base64 string, including recalculating checksum"""
    result = bytearray()
    result.extend(header)
    result.append(gradient_flag)
    result.append(points)
    for r, g, b in colors:
        result.extend([r, g, b])
    checksum = calculate_checksum(result)
    result.append(checksum)
    return base64.b64encode(result).decode('ascii')

# Example usage
b64_input = 'MwUEzycAAAAAAAAAAAAAAAAAANo='

# Decode
header, gradient_flag, points, colors = decode_colors(b64_input)

print("Header:", list(header))
print("Gradient Flag:", gradient_flag)
print("Points (LED count):", points)
print("Colors:")
for idx, color in enumerate(colors):
    print(f"{idx}: {color}")

# Modify a color
colors[0] = (0, 255, 0)  # set first LED to green

# Encode back
new_b64 = encode_colors(header, gradient_flag, points, colors)
print("\nModified Base64:")
print(new_b64)
