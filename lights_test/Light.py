from copy import deepcopy
from light_types import lightTypes
import uuid
import random
import logManager
import wled
import native_multi
import homeassistant_ws

protocols = [wled, native_multi, homeassistant_ws]

logging = logManager.logger.get_logger(__name__)

def genV2Uuid():
    return str(uuid.uuid4())

def generate_unique_id():
    rand_bytes = [random.randrange(0, 256) for _ in range(3)]
    return "00:17:88:01:00:%02x:%02x:%02x-0b" % (rand_bytes[0], rand_bytes[1], rand_bytes[2])

class Light():
    def __init__(self, data):
        self.name = data["name"]
        self.modelid = data["modelid"]
        self.id_v1 = data["id_v1"]
        self.id_v2 = data["id_v2"] if "id_v2" in data else genV2Uuid()
        self.uniqueid = data["uniqueid"] if "uniqueid" in data else generate_unique_id()
        self.state = data["state"] if "state" in data else deepcopy(lightTypes[self.modelid]["state"])
        self.protocol = data["protocol"] if "protocol" in data else "dummy"
        self.config = data["config"] if "config" in data else deepcopy(lightTypes[self.modelid]["config"])
        self.protocol_cfg = data["protocol_cfg"] if "protocol_cfg" in data else {}
        self.streaming = False
        self.dynamics = deepcopy(lightTypes[self.modelid]["dynamics"])
        self.effect = "no_effect"
        self.function = data["function"] if "function" in data else "mixed"
        self.controlled_service = data["controlled_service"] if "controlled_service" in data else "manual"

    def save(self):
        result = {"id_v2": self.id_v2, "name": self.name, "modelid": self.modelid, "uniqueid": self.uniqueid, "function": self.function,
                  "state": self.state, "config": self.config, "protocol": self.protocol, "protocol_cfg": self.protocol_cfg}
        return result
    
    def get_info(self):
        return {
            "name": self.name,
            "modelid": self.modelid,
            "protocol": self.protocol,
            "protocol_cfg": self.protocol_cfg}
    
    def getV1Api(self):
        result = lightTypes[self.modelid]["v1_static"]
        result["config"] = self.config
        result["state"] = {"on": self.state["on"]}
        if "bri" in self.state and self.modelid not in ["LOM001", "LOM004", "LOM010"]:
            result["state"]["bri"] = int(self.state["bri"]) if self.state["bri"] is not None else 1
        if "ct" in self.state and self.modelid not in ["LOM001", "LOM004", "LOM010", "LTW001", "LLC010"]:
            result["state"]["ct"] = self.state["ct"]
            result["state"]["colormode"] = self.state["colormode"]
        if "xy" in self.state and self.modelid not in ["LOM001", "LOM004", "LOM010", "LTW001", "LWB010"]:
            result["state"]["xy"] = self.state["xy"]
            result["state"]["hue"] = self.state["hue"]
            result["state"]["sat"] = self.state["sat"]
            result["state"]["colormode"] = self.state["colormode"]
        result["state"]["alert"] = self.state["alert"]
        if "mode" in self.state:
            result["state"]["mode"] = self.state["mode"]
        result["state"]["reachable"] = self.state["reachable"]
        result["modelid"] = self.modelid
        result["name"] = self.name
        result["uniqueid"] = self.uniqueid
        return result
    
    def incProcess(self, state, data):
        if "bri_inc" in data:
            state["bri"] += data["bri_inc"]
            if state["bri"] > 254:
                state["bri"] = 254
            elif state["bri"] < 1:
                state["bri"] = 1
            del data["bri_inc"]
            data["bri"] = state["bri"]
        elif "ct_inc" in data:
            state["ct"] += data["ct_inc"]
            if state["ct"] > 500:
                state["ct"] = 500
            elif state["ct"] < 153:
                state["ct"] = 153
            del data["ct_inc"]
            data["ct"] = state["ct"]
        elif "hue_inc" in data:
            state["hue"] += data["hue_inc"]
            if state["hue"] > 65535:
                state["hue"] -= 65535
            elif state["hue"] < 0:
                state["hue"] += 65535
            del data["hue_inc"]
            data["hue"] = state["hue"]
        elif "sat_inc" in data:
            state["sat"] += data["sat_inc"]
            if state["sat"] > 254:
                state["sat"] = 254
            elif state["sat"] < 1:
                state["sat"] = 1
            del data["sat_inc"]
            data["sat"] = state["sat"]

        return data
    
    def updateLightState(self, state):

        if "xy" in state and "xy" in self.state:
            self.state["colormode"] = "xy"
        elif "ct" in state and "ct" in self.state:
            self.state["colormode"] = "ct"
        elif ("hue" in state or "sat" in state) and "hue" in self.state:
            self.state["colormode"] = "hs"
    
    def setV1State(self, state):
        if "lights" not in state:
            state = self.incProcess(self.state, state)
            self.updateLightState(state)
            for key, value in state.items():
                if key in self.state:
                    self.state[key] = value
                if key in self.config:
                    if key == "archetype":
                        self.config[key] = value.replace("_","")
                    else:
                        self.config[key] = value
                if key == "name":
                    self.name = value
                if key == "function":
                    self.function = value
            if "bri" in state:
                if "min_bri" in self.protocol_cfg and self.protocol_cfg["min_bri"] > state["bri"]:
                    state["bri"] = self.protocol_cfg["min_bri"]
                if "max_bri" in self.protocol_cfg and self.protocol_cfg["max_bri"] < state["bri"]:
                    state["bri"] = self.protocol_cfg["max_bri"]

        for protocol in protocols:
            if self.protocol == protocol.__name__:
                try:
                    protocol.set_light(self, state)
                    self.state["reachable"] = True
                except Exception as e:
                    self.state["reachable"] = False
                    logging.warning(self.name + " light error, details: %s", e)
