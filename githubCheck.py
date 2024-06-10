import requests
import json
from datetime import datetime

def DiyHueCheck():
    diyhue_url = "https://api.github.com/repos/diyhue/diyhue/branches/master"
    #url = "https://api.github.com/repos/hendriksen-mark/diyhue/branches/master"
    diyhue = requests.get(diyhue_url)

    if diyhue.status_code == 200:
        diyhue_data = json.loads(diyhue.text)
        diyhue_time = datetime.strptime(diyhue_data["commit"]["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

    return diyhue_time

def UICheck():
    ui_url = "https://api.github.com/repos/diyhue/diyHueUI/releases/latest"
    #ui_url = "https://api.github.com/repos/hendriksen-mark/diyHueUI/releases/latest"
    ui = requests.get(ui_url)

    if ui.status_code == 200:
        ui_data = json.loads(ui.text)
        ui_time = datetime.strptime(ui_data["published_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

    return ui_time

def PhilipsCheck():
    new = {}
    philips_url = "https://firmware.meethue.com/v1/checkupdate/?deviceTypeId=BSB002&version=0"
    philips = requests.get(philips_url)

    if philips.status_code == 200:
        device_data = json.loads(philips.text)
        if len(device_data["updates"]) != 0:
            new["version"] = str(device_data["updates"][len(device_data["updates"])-1]["version"])
            new["versionName"] = str(device_data["updates"][len(device_data["updates"])-1]["versionName"][:4]+".0")
    return new

print("DiyHue published: " + DiyHueCheck())
print("UI published:     " + UICheck())
print("SW version:       " + PhilipsCheck()["version"])
print("API version:      " + PhilipsCheck()["versionName"])