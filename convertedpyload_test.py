standardSensors = {}
standardSensors = {
    "RDM002": {
        "dataConversion": {
            "rootKey": "action",
            "dirKey": "action_direction",
            "typeKey": "action_type",
            "timeKey": "action_time",
            "button_1_press": {"buttonevent": 1000},
            "button_1_hold": {"buttonevent": 1001},
            "button_1_press_release": {"buttonevent": 1002},
            "button_1_hold_release": {"buttonevent": 1003},
            "button_2_press": {"buttonevent": 2000},
            "button_2_hold": {"buttonevent": 2001},
            "button_2_press_release": {"buttonevent": 2002},
            "button_2_hold_release": {"buttonevent": 2003},
            "button_3_press": {"buttonevent": 3000},
            "button_3_hold": {"buttonevent": 3001},
            "button_3_press_release": {"buttonevent": 3002},
            "button_3_hold_release": {"buttonevent": 3003},
            "button_4_press": {"buttonevent": 4000},
            "button_4_hold": {"buttonevent": 4001},
            "button_4_press_release": {"buttonevent": 4002},
            "button_4_hold_release": {"buttonevent": 4003},
            "dial_rotate_left_step": {"rotaryevent": 1},
            "dial_rotate_left_slow": {"rotaryevent": 2},
            "dial_rotate_left_fast": {"rotaryevent": 2},
            "dial_rotate_right_step": {"rotaryevent": 1},
            "dial_rotate_right_slow": {"rotaryevent": 2},
            "dial_rotate_right_fast": {"rotaryevent": 2},
        }
    }
}
test = str(standardSensors["RDM002"]["dataConversion"]["button_4_hold_release"]["buttonevent"])[:1]
#print(test)
import os
print(os.times())
print(os.uname())


response = "posix.uname_result(sysname='Linux', nodename='raspberrypi', release='6.6.20+rpt-rpi-2712', version='#1 SMP PREEMPT Debian 1:6.6.20-1+rpt1 (2024-03-07)', machine='aarch64')"
#posix.uname_result(sysname='Darwin', nodename='MBP-van-Mark.lan', release='23.3.0', version='Darwin Kernel Version 23.3.0: Wed Dec 20 21:28:58 PST 2023; root:xnu-10002.81.5~7/RELEASE_X86_64', machine='x86_64')
#print(response)