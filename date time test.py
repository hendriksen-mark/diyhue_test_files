from datetime import datetime, timezone

creation_time = "2024-02-18 19:50:15.000000 +0100\n"
creation_time_arg1 = creation_time.replace(".", " ").split(" ")#2024-02-18, 19:50:15, 000000000, +0100\n
creation_time = creation_time_arg1[0] + " " + creation_time_arg1[1] + " " + creation_time_arg1[3].replace("\n", "")#2024-02-18 19:50:15 +0100
creation_time = datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S %z").astimezone(timezone.utc).strftime("%Y-%m-%d %H")

print(creation_time)
