import uuid
from datetime import datetime, timezone
import logManager
from time import sleep
import json

logging = logManager.logger.get_logger(__name__)

eventstream = []
def StreamEvent(message):
    if type(message) is list:
        global eventstream
        eventstream = message
    else:
        eventstream.append(message)

light_streamMessage = {"creationtime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "data":[],
                                 "id": str(uuid.uuid4()),
                                 "type": "update"
                                 }
for num in range(4):
        light_streamMessage["data"].insert(num,{
             "id": num,
             "id_v1": "/lights/" + str(num),
             "owner": {
                  "rid": num,
                  "rtype":"device"
            },
            "service_id": 0,
            "type": "light"
                })
        light_streamMessage["data"][num].update({"on": {"on": False}})
#StreamEvent(light_streamMessage)


group_streamMessage = {"creationtime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "data": [{"id": 1,"id_v1": "/groups/", "type": "grouped_light",
                                   "owner": {
                                       "rid": "id",
                                       "rtype": "room"
                                   }
                                   }],
                         "id": str(uuid.uuid4()),
                         "type": "update"
                         }
group_streamMessage["data"][0].update({"on": {"on": False}})
#StreamEvent(group_streamMessage)
streamMessage = []
streamMessage.append(light_streamMessage)
streamMessage.append(group_streamMessage)
#print(type(streamMessage))

StreamEvent(streamMessage)


if len(eventstream) > 0:
    for index, messages in enumerate(eventstream):
                    logging.debug(json.dumps([messages], separators=(',', ':')))
    sleep(0.3)  # ensure all devices connected receive the events
    eventstream = []
    sleep(0.2)