sensorTypes = {}
sensorTypes["SML001"] = {"ZLLTemperature" : {"state": {"temperature": 2100,"lastupdated": "none"},"config": {"on": False,"battery": 100,"reachable": True,"alert": "none","ledindication": False,"usertest": False,"pending": []}, "static": {"swupdate": {"state": "noupdates","lastinstall": "2021-03-16T21:16:40Z"}, "manufacturername": "Signify Netherlands B.V.","productname": "Hue temperature sensor","swversion": "6.1.1.27575","capabilities": {"certified": True,"primary": False}}},
                        "ZLLPresence" : { "state": {"lastupdated": "none","presence": None  }, "config": {"on": False,"battery": 100,"reachable": True,"alert": "none","ledindication": False,"usertest": False,"sensitivity": 2,"sensitivitymax": 2,"pending": []  }, "static": {"swupdate": {"state": "noupdates","lastinstall": "2021-03-16T21:16:40Z"}, "manufacturername": "Signify Netherlands B.V.", "productname": "Hue motion sensor", "swversion": "6.1.1.27575", "capabilities":{"certified":True,"primary":True}}},
                        "ZLLLightLevel" : {"state": {"dark": True,"daylight": False,"lightlevel": 6000,"lastupdated": "none"}, "config": {"on": False,"battery": 100,"reachable": True,"alert": "none","tholddark": 9346,"tholdoffset": 7000,"ledindication": False,"usertest": False,"pending": []}, "static": {"swupdate": {  "state": "noupdates",  "lastinstall": "2021-03-16T21:16:40Z"}, "manufacturername": "Signify Netherlands B.V.","productname": "Hue ambient light sensor","swversion": "6.1.1.27575","capabilities": {  "certified": True,  "primary": False}}}}

temp = sensorTypes["SML001"]["ZLLTemperature"]["state"]["temperature"]
if type(temp) == int:
    print(type(temp))
else:
    print("non int")