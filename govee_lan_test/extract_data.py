import json
import os
import binascii
import base64

data_data = []
# Load the JSON file
with open(os.path.join(os.path.dirname(__file__), 'govee1.json'), 'r') as file:
    data = json.load(file)

# Extract the "data.data" field
for item in data:
    if "_source" in item and "layers" in item["_source"] and "data" in item["_source"]["layers"]:
        if "data.data" in item["_source"]["layers"]["data"]:
            hex_message = item["_source"]["layers"]["data"]["data.data"].replace(":", "")
            decoded_message = binascii.unhexlify(hex_message).decode('utf-8')
            decoded_json = json.loads(decoded_message)
            if "msg" in decoded_json and "data" in decoded_json["msg"] and "pt" in decoded_json["msg"]["data"]:
                data_data.append(decoded_json["msg"]["data"]["pt"])

# Output the extracted value
if data_data:
    print("Extracted 'data.data'")
    #print("Extracted 'data.data':", json.dumps(data_data, indent=4))
else:
    print("No 'data.data' found.")

# Save the extracted data to a file
output_file = os.path.join(os.path.dirname(__file__), 'extracted_data.json')
with open(output_file, 'w') as outfile:
    json.dump(data_data, outfile, indent=4)

print(f"Extracted data saved to {output_file}")
