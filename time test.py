import time
import os

os.environ['TZ'] = 'Singapore'

time.tzset()

print(time.strftime('%X %x %Z'))