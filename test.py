import os
import uuid
import re

def get_device_details():
    # Get device/computer name
    device_name = os.environ.get('USER')
    print(os.environ)
    print(f"Device Name: {device_name}")

    # Get MAC address
    mac_addr = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    print(f"MAC Address: {mac_addr}")

if __name__ == "__main__":
    get_device_details()