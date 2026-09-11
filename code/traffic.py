import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = b"0" * 60000
interval = 0.0005

print("Sending continuous UDP traffic... Ctrl+C to stop")

while True:
    s.sendto(data, ("snmp-device-2", 9999))
    time.sleep(interval)