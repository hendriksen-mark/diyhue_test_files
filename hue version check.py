import requests
import json

modelid = "BSB002"
swversion = "1972154010"
#swversion = "1947108030"
#swversion = "1033989"
#swversion = "0"

url = "https://firmware.meethue.com/v1/checkupdate/?deviceTypeId=BSB002&version=0"
#url = "https://firmware.meethue.com/v1/checkupdate/?deviceTypeId=" + modelid + "&version=" + swversion
response = requests.get(url)

if response.status_code == 200:
    device_data = json.loads(response.text)
    if len(device_data["updates"]) != 0:
        print("update")
        new_version = str(device_data["updates"][len(device_data["updates"])-1]["version"])
        new_versionName = str(device_data["updates"][len(device_data["updates"])-1]["versionName"][:4]+".0")
        print(new_version)
        print(new_versionName)
        if new_version > swversion:
            print("swversion number update from Philips")
        elif swversion > new_version:
            print("swversion higher than Philips")
        else:
            print("no update")
    else:
        print("no update")
