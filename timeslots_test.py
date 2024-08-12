from astral.sun import sun
from astral import LocationInfo
from datetime import datetime, timezone
import logManager
from threading import Thread
from time import sleep

logging = logManager.logger.get_logger(__name__)

lat = 52.1
long = 5.2
tz = "Europe/Amsterdam"

localzone = LocationInfo('localzone', tz.split("/")[1], tz, lat, long)


s = sun(localzone.observer, date=datetime.now(timezone.utc))
sunset = s['sunset'].astimezone().strftime("%H:%M:%S")
#print(sunset)
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
                        "time": {"hour": 7, "minute": 0, "second": 0},
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
                        "time": {"hour": 10, "minute": 0, "second": 0},
                    },
                    "target":
                    {
                        "rid": "f2ab39ae-2f6c-4d78-a67e-08e08b2bad16",
                        "rtype": "scene",
                    },
                },
                {
                    "start_time": {"kind": "sunset"},
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
                        "time": {"hour": 20, "minute": 0, "second": 0},
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
                        "time": {"hour": 22, "minute": 0, "second": 0},
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

slots = result["week_timeslots"][0]["timeslots"]

# smartscene = result["week_timeslots"][0]["timeslots"]
# print("smartscen: ")
# print(smartscene)
def test():
    active_timeslot = 0
    while True:
        for instance, slot in enumerate(result["week_timeslots"][0]["timeslots"]):
            time_object = ""
            test_object = datetime(
                    year=datetime.now().year,
                    month=datetime.now().month,
                    day=datetime.now().day,
                    hour=2,
                    minute=0,
                    second=0)
            if slot["start_time"]["kind"] == "time":
                time_object = datetime(
                    year=datetime.now().year,
                    month=datetime.now().month,
                    day=datetime.now().day,
                    hour=slot["start_time"]["time"]["hour"],# if slot["start_time"]["time"]["hour"] > 0 else 23,
                    minute=slot["start_time"]["time"]["minute"],# if slot["start_time"]["time"]["hour"] > 0 else 59,
                    second=slot["start_time"]["time"]["second"])# if slot["start_time"]["time"]["hour"] > 0 else 59)
            elif slot["start_time"]["kind"] == "sunset":
                #datetime.strptime(sunset, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
                time_object = datetime(
                    year=datetime.now().year,
                    month=datetime.now().month,
                    day=datetime.now().day,
                    hour=int(datetime.strptime(sunset, "%H:%M:%S").strftime("%H")),
                    minute=int(datetime.strptime(sunset, "%H:%M:%S").strftime("%M")),
                    second=int(datetime.strptime(sunset, "%H:%M:%S").strftime("%S")))
                print(time_object)
            if test_object.second >= time_object.second and test_object.minute >= time_object.minute and test_object.hour >= time_object.hour:
                active_timeslot = instance
        print(active_timeslot)
        print(result["week_timeslots"][0]["timeslots"][active_timeslot]["target"]["rid"])
        sleep(0.5)
    #print(time_object)
#test()
print(slots)
#Thread(target=test).start()
#print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#print(active_timeslot)
#print(result["week_timeslots"][0]["timeslots"][active_timeslot]["start_time"]["time"]["hour"])
#print(result["week_timeslots"][0]["timeslots"][active_timeslot]["target"]["rtype"])
#print(len(result["week_timeslots"][0]["timeslots"]))
 #obj.timeslots[active_timeslot]["start_time"]["time"]["hour"]
    #print(instance)
    #print(slot["target"]["rtype"])
    #print(slot["target"]["rid"])
    #print(result["transition_duration"])

# for smartscene in result["week_timeslots"]:

    # print("smartscen: ")
    # print(smartscene["timeslots"])
    # print(result["week_timeslots"]["timeslots"][smartscene])
    # print("obj: ")
    # print(obj)
