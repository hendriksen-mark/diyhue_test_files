from astral.sun import sun
from astral import LocationInfo
from datetime import datetime, timezone, timedelta
import logManager
from time import sleep
from copy import deepcopy

logging = logManager.logger.get_logger(__name__)

lat = 52.1
long = 5.2
tz = "Europe/Amsterdam"

localzone = LocationInfo('localzone', tz.split("/")[1], tz, lat, long)


s = sun(localzone.observer, date=datetime.now(timezone.utc))
sunset = s['sunset'].astimezone().strftime("%H:%M:%S")

result = {
    "metadata":
    {
        "name": "Natuurlijk licht",
        "image":
        {
            "rid": "eb014820-a902-4652-8ca7-6e29c03b87a1",
            "rtype": "public_image",
        },
    },
    "group": {"rid": "46332c14-1c72-5fe3-b817-9621e535a68b", "rtype": "room"},
    "week_timeslots":
    [
        {
            "timeslots":
            [
                {
                    "start_time":
                    {
                        "kind": "time",
                        "time": {"hour": 7, "minute": 5, "second": 0},
                    },
                    "target":
                    {
                        "rid": "43b3b7c2-eb23-4e72-9628-20d73507d7bc",
                        "rtype": "scene",
                    },
                },
                {
                    "start_time":
                    {
                        "kind": "time",
                        "time": {"hour": 10, "minute": 25, "second": 0},
                    },
                    "target":
                    {
                        "rid": "f2ab39ae-2f6c-4d78-a67e-08e08b2bad16",
                        "rtype": "scene",
                    },
                },
                {
                    "start_time": 
                    {
                        "kind": "sunset",
                    },
                    "target":
                    {
                        "rid": "66d4471f-6b1a-4151-a38c-f421d07e2b13",
                        "rtype": "scene",
                    },
                },
                {
                    "start_time":
                    {
                        "kind": "time",
                        "time": {"hour": 20, "minute": 30, "second": 30},
                    },
                    "target":
                    {
                        "rid": "b1fb3678-aa27-4da0-8baf-10b42f46d820",
                        "rtype": "scene",
                    },
                },
                {
                    "start_time":
                    {
                        "kind": "time",
                        "time": {"hour": 22, "minute": 3, "second": 0},
                    },
                    "target":
                    {
                        "rid": "0e098d29-2ccd-4043-8de4-30412637cd25",
                        "rtype": "scene",
                    },
                },
                {
                    "start_time":
                    {
                        "kind": "time",
                        "time": {"hour": 0, "minute": 0, "second": 0},
                    },
                    "target":
                    {
                        "rid": "d564f1fd-cb53-4de6-90ad-96502a044377",
                        "rtype": "scene",
                    },
                },
            ],
            "recurrence":
            [
                "sunday",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
            ],
        },
    ],
    "transition_duration": 60000,
    "recall": {"action": "activate"},
}
#logging.debug(result["week_timeslots"][0]["timeslots"][-1])

slots = deepcopy(result["week_timeslots"][0]["timeslots"])
sunset_slot = -1
for instance, slot in enumerate(slots):
    if slot["start_time"]["kind"] == "time":
        time_object = datetime(
            year=1,
            month=1,
            day=1,
            hour=slot["start_time"]["time"]["hour"],
            minute=slot["start_time"]["time"]["minute"],
            second=slot["start_time"]["time"]["second"]).strftime("%H:%M:%S")
    elif slot["start_time"]["kind"] == "sunset":
        sunset_slot = instance
        time_object = sunset
    if sunset_slot > 0 and instance == sunset_slot+1:
        if sunset > time_object:
            time_object = (datetime.strptime(sunset, "%H:%M:%S") + timedelta(minutes=30)).strftime("%H:%M:%S")
    slots[instance]["start_time"]["time"] = time_object
    slots[instance]["start_time"]["instance"] = instance

# logging.debug(slots)
slots = sorted(slots, key=lambda x: datetime.strptime(x["start_time"]["time"], "%H:%M:%S"))
logging.debug(slots)
# logging.debug(result)
test = 1
active_timeslot = test
prev_timeslot = -1
while True:
    for slot in slots:
        if datetime.now().strftime("%H:%M:%S") >= slot["start_time"]["time"]:
            active_timeslot = slot["start_time"]["instance"]
    if prev_timeslot != active_timeslot:
        prev_timeslot = active_timeslot
        # logging.debug(test)
        logging.debug(active_timeslot)
    sleep(0.5)

