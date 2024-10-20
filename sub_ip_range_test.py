sub_ip_range_start = 1
sub_ip_range_end = 10
ip_range_start = 1
ip_range_end = 10
host_ip = "192.168.1.25"

for sub_addr in range(sub_ip_range_start, sub_ip_range_end + 1):
    print(sub_addr)

print("IP range for light discovery: " + str(host_ip.split('.')[0]) + "." + str(host_ip.split('.')[1]) + "." + str(sub_ip_range_start) + "." + str(ip_range_start) + "-" + str(host_ip.split('.')[0]) + "." + str(host_ip.split('.')[1]) + "." + str(sub_ip_range_end) + "." + str(ip_range_end))