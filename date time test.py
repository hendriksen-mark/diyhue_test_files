from datetime import datetime, timezone

creation_time = "2024-02-18 19:50:15.000000 +0100\n"
#creation_time = "2024-02-18 19:50:15.000000\n"
creation_time_arg1 = creation_time.replace(".", " ").split(" ")#2024-02-18, 19:50:15, 000000000, +0100\n
print(len(creation_time_arg1))
if (len(creation_time_arg1) < 4):
    creation_time = creation_time_arg1[0] + " " + creation_time_arg1[1].replace("\n", "")#2024-02-18 19:50:15
    creation_time = datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S").astimezone(timezone.utc).strftime("%Y-%m-%d %H")#2024-02-18 18
else:
    creation_time = creation_time_arg1[0] + " " + creation_time_arg1[1] + " " + creation_time_arg1[3].replace("\n", "")#2024-02-18 19:50:15 +0100
    creation_time = datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S %z").astimezone(timezone.utc).strftime("%Y-%m-%d %H")#2024-02-18 18

print(creation_time)

print(datetime.now().strftime("T%H:%M:%S"))
while True:
    if (datetime.now().strftime("T%H:%M:%S") == "T23:24:00"):
        print("true")