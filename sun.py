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

logging.debug("Sunset: " + str(deltaSunset))
logging.debug("Sunrise: " + str(deltaSunrise))