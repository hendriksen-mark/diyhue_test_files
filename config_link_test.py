config = {}
config["linkbutton"] = True

if "linkbutton" not in config or type(config["linkbutton"]) == bool or "lastlinkbuttonpushed" not in config["linkbutton"]:
    config["linkbutton"] = {"lastlinkbuttonpushed": 1599398980}

print(config)