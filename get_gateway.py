import subprocess

result = subprocess.run(["ip route | grep default | head -n 1 | cut -d ' ' -f 3"], shell=True, capture_output=True, text=True)
ip_pieces = result.stdout.split(".")
gateway = ip_pieces[0] + "." + ip_pieces[1] + "." + ip_pieces[2] + "." + ip_pieces[3].replace("\n", "")

print(gateway)
