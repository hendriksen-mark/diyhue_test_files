from subprocess import check_output

host_ip = "192.168.1.25"

test_mac = "xx:xx:xx:xx:xx:xx"
test_mac1 = "xx:xx:xx:xx:xx:xx"

if test_mac and str(test_mac).replace(":", "").upper() != "XXXXXXXXXXXX":
    mac = test_mac
elif test_mac1 and str(test_mac1).replace(":", "").upper() != "XXXXXXXXXXXX":
    mac = test_mac1
else:
    mac = check_output("cat /sys/class/net/$(ip -o addr | grep -w %s | awk '{print $2}')/address" % host_ip,
                                 shell=True).decode('utf-8')[:-1]

if mac == "xx:xx:xx:xx:xx:xx" or mac == "":
    print("No valid MAC address provided " + str(mac))
    print("To fix this visit: https://diyhue.readthedocs.io/en/latest/getting_started.html")
    raise ValueError("mac == " + str(mac))
else:
    print("Host MAC given as " + mac + " " + mac.upper())