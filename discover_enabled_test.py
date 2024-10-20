config = {}
config["config"] = {
    #"hue": {"ip": "ip", "hueUser": "hueUser", "hueKey": "hueKey" },
    "hue": {},
    "shelly": {"enabled":True},
    }

if config["config"]["shelly"]["enabled"]:
    print("shelly anabled")

if config["config"]["hue"]:
    print("hue anabled")
    print(config["config"]["hue"])
