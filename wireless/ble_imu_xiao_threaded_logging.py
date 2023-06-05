from bluepy import btle
import time
import struct
import binascii
from time import sleep

import threading
from threading import Thread



# Have to match with peripheral:def read_ble_char(char):
def read_ble_char(characteristics):
	counter = 0
	while True:
		for char in characteristics:
			if char.uuid == CHARACTERISTIC_UUID:
				s = struct.Struct("f f f")
				unpacked_data = s.unpack(char.read())
				counter += 1
				print("Data Length: ", counter, " | New Data: ", unpacked_data)


MAC = "ee:7a:ec:0e:56:67"
SERVICE_UUID = "1101"
CHARACTERISTIC_UUID = "2101"


print("Hello!")

print("Connect to: " + MAC)
dev = btle.Peripheral(MAC)

print("\n--- dev ----------------------")
print(type(dev))

print("\n--- dev.services ------------------")
for svc in dev.services:
	print(str(svc))

print("\n--------------------------------")
print("Get service by UUID: " + SERVICE_UUID)
service_uuid = btle.UUID(SERVICE_UUID)
service = dev.getServiceByUUID(service_uuid)

#-----------------------------------------
characteristics = dev.getCharacteristics()
# print("\n--- dev.getCharacteristics() ----------------")
# print(type(characteristics))
# print(characteristics)

# for char in characteristics:
# 	print("------------------")
# 	print(type(char))
# 	print(char.uuid)
# 	if char.uuid == CHARACTERISTIC_UUID:
# 		snooziness = int(input("Enter IMU Signal Sampling Period: >"))
# 		imu_sampling_thread.start()
# 		sleep(snooziness)


imu_sampling_period = int(input("Enter IMU Sampling Period: >"))

imu_sampling_thread = threading.Thread(target = read_ble_char, args=(characteristics,))
imu_sampling_thread.daemon = True
imu_sampling_thread.start()
sleep(imu_sampling_period)


	


