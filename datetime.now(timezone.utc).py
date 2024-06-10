from datetime import datetime, timedelta, time, date, timezone
lu = "2024-04-09T20:00:52"
lu = datetime.strptime(lu, "%Y-%m-%dT%H:%M:%S")
#print(abs(datetime.now(timezone.utc).replace(tzinfo=None) - lu))

timmer = "10:10:10"
(h, m, s) = timmer.split(':')
d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
print((datetime.now(timezone.utc).replace(tzinfo=None) - d).replace(microsecond=0).isoformat())
print(datetime.now(timezone.utc).replace(tzinfo=None).replace(microsecond=0).isoformat())