import requests
import json
import subprocess
from datetime import datetime, timezone

#creation_time = subprocess.run("stat -c %y HueEmulator3.py", shell=True, capture_output=True, text=True)
#publish_time = ""

#url = "https://api.github.com/repos/diyhue/diyhue/branches/master"
url = "https://api.github.com/repos/hendriksen-mark/diyhue/branches/master"
#url = "https://api.github.com/repos/diyhue/diyHueUI/releases/latest"
response = requests.get(url)

if response.status_code == 200:
    device_data = json.loads(response.text)
    print(device_data["published_at"])
    #publish_time = device_data["commit"]["commit"]["author"]["date"]
    #publish_time = datetime.strptime(device_data["commit"]["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H")
    publish_time = datetime.strptime(device_data["published_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H")

#print(creation_time)
print(publish_time)
