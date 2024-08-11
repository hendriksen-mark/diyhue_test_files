import time
import os

os.environ['TZ'] = 'America/Detroit'

time.tzset()

print(time.strftime('%X %x %Z'))