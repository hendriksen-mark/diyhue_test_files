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

logging.debug("Sunset: " + datetime.strptime(str(s['sunset']), "%Y-%m-%d %H:%M:%S.%f%z").astimezone().strftime("%H:%M:%S"))
logging.debug("Sunrise: " + datetime.strptime(str(s['sunrise']), "%Y-%m-%d %H:%M:%S.%f%z").astimezone().strftime("%H:%M:%S"))
logging.debug("deltaSunset: " + str(deltaSunset))
logging.debug("deltaSunrise: " + str(deltaSunrise))