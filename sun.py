from astral.sun import sun
from astral import LocationInfo
from datetime import datetime, timezone
import logManager

logging = logManager.logger.get_logger(__name__)

lat = 52.1
long = 5.2
tz = "Europe/Amsterdam"

localzone = LocationInfo('localzone', tz.split("/")[1], tz, lat, long)


s = sun(localzone.observer, date=datetime.now(timezone.utc))
deltaSunset = s['sunset'].replace(tzinfo=None) - datetime.now(timezone.utc).replace(tzinfo=None)
deltaSunrise = s['sunrise'].replace(tzinfo=None) - datetime.now(timezone.utc).replace(tzinfo=None)
sunset = s['sunset'].astimezone()
#time_object = datetime.strptime(sunset, "%Y-%m-%d %H:%M:%S%z").astimezone().strftime("%Y-%m-%d %H:%M:%S")#2024-02-18 18
logging.debug(sunset.strftime("%H:%M:%S"))
logging.debug(sunset.strftime("%Y-%m-%d %H:%M:%S"))

time_object = datetime(
    year=1,
    month=2,
    day=3,
    hour=4,
    minute=5,
    second=6)
logging.debug(time_object)



#logging.debug("Sunset: " + datetime.strptime(str(s['sunset']), "%Y-%m-%d %H:%M:%S.%f%z").astimezone().strftime("%H:%M:%S"))
#logging.debug("Sunrise: " + datetime.strptime(str(s['sunrise']), "%Y-%m-%d %H:%M:%S.%f%z").astimezone().strftime("%H:%M:%S"))
#logging.debug("deltaSunset: " + str(deltaSunset))
#logging.debug("deltaSunrise: " + str(deltaSunrise))
#logging.debug("sunset" in s)