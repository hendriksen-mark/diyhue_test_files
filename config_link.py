config = {"linkbutton": {"lastlinkbuttonpushed": 0}}


if "linkbutton" not in config or type(config["linkbutton"]) == bool or "lastlinkbuttonpushed" not in config["linkbutton"]:
    config["linkbutton"] = {"lastlinkbuttonpushed": 1599398980}

#print(config)

bridge_id = "2CCF67FFFE0EBD6B"

print(bridge_id[-6:])