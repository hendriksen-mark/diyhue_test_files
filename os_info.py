import os
import json
import subprocess
response = {}


#response = "posix.uname_result(sysname='Linux', nodename='raspberrypi', release='6.6.20+rpt-rpi-2712', version='#1 SMP PREEMPT Debian 1:6.6.20-1+rpt1 (2024-03-07)', machine='aarch64')"
#posix.uname_result(sysname='Darwin', nodename='MBP-van-Mark.lan', release='23.3.0', version='Darwin Kernel Version 23.3.0: Wed Dec 20 21:28:58 PST 2023; root:xnu-10002.81.5~7/RELEASE_X86_64', machine='x86_64')
#print(response)
response["sysname"] = os.uname().sysname
response["machine"] = os.uname().machine
response["os_version"] = os.uname().version
response["os_release"] = os.uname().release
response["diyhue"] = subprocess.run("stat -c %y HueEmulator3.py", shell=True, capture_output=True, text=True).stdout.replace("\n", "")
 
print(response)