import binascii
import json
import base64

# Hex message
#hex_message = "7b226d7367223a7b22636d64223a2272617a6572222c2264617461223a7b227074223a22757741677341454b737333677574586f76646675774e6a74314f6e382f507a385c7530303242666e375c75303032422f76375c75303032427672367975446c51513d3d227d7d7d"
#hex_message = "7b226d7367223a7b22636d64223a2272617a6572222c2264617461223a7b227074223a22757741677341454b2f7741412f7741412f7741412f7741412f7741412f7741412f7741412f7741412f7741412f77414149413d3d227d7d7d"
#hex_message = "7b226d7367223a7b22636d64223a2272617a6572222c2264617461223a7b227074223a22757741427351454b227d7d7d"
#hex_message = "7b226d7367223a7b22636d64223a2272617a6572222c2264617461223a7b227074223a22757741677341454b7574547277393330794f543679655035314f6e38344f4c69335c7530303242486a36656e7034754467795c7530303242446d63413d3d227d7d7d"
# Step 1: Convert hex to ASCII
#ascii_message = binascii.unhexlify(hex_message).decode('utf-8')

# Step 2: Parse as JSON
#decoded_json = json.loads(ascii_message)

# Output the result
#print("Decoded JSON:", decoded_json)
#{'msg': {'cmd': 'razer', 'data': {'pt': 'uwAgsAEKss3gutXovdfuwNjt1On8/Pz8+fn7+/v7+vr6yuDlQQ=='}}}
#{'msg': {'cmd': 'razer', 'data': {'pt': 'uwAgsAEK /wAA /wAA /wAA /wAA /wAA /wAA /wAA /wAA /wAA /wAA IA=='}}}
#decoded_json = {"msg":{"cmd":"razer","data":{"pt":"uwAgsAEKmUb/mUb/mUb/mUb/mUb/Rf86Rf86Rf86Rf86Rf86gA=="}}}
decoded_json = {"msg":{"cmd":"razer","data":{"pt":"uwAgsAEKmUb/mUb/mUb/mUb/mUb/mUb/Rf86Rf86Rf86Rf86IA=="}}}
#decoded_json = {"msg":{"cmd":"ptReal","data":{"command":["MwUEzycAAAAAAAAAAAAAAAAAANo="]}}}

# Base64 decode the "pt" field
pt_value = decoded_json["msg"]["data"]["pt"]
print("'pt' Value (without prefix):", pt_value.replace("uwAgsAEK", ""))
print("Base64 'pt' Value (without prefix):", base64.b64decode(pt_value.replace("uwAgsAEK", "")))
decoded_pt = base64.b64decode(pt_value)

print("Base64 Decoded 'pt':", decoded_pt)

# RGB values as 10 hex colors of 24-bit
hex_colors = [
    0xFFFFFF, 0x00FF00, 0x0000FF,  # Example colors: Red, Green, Blue
    0xFFFF00, 0xFF00FF, 0x00FFFF,  # Yellow, Magenta, Cyan
    0x800000, 0x808000, 0x008080,  # Maroon, Olive, Teal
    0x000080  # Navy
]

# Convert hex colors to Base64 encoded 24-bit values
base64_colors = [
    base64.b64encode(bytes([(color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF])).decode('utf-8')
    for color in hex_colors
]
print("Base64 Encoded Colors:", base64_colors)

# Create the new `pt` value starting with "uwAgsAEK" followed by the Base64-encoded colors
modified_pt_base64 = "uwAgsAEK" + "".join(base64_colors)

# Update the JSON with the modified 'pt' value
decoded_json["msg"]["data"]["pt"] = modified_pt_base64

# Output the updated JSON
print("Updated JSON:", json.dumps(decoded_json))