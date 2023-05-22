from bluepy import btle
import time
import struct
import binascii

# Have to match with peripheral:
MAC = "2d:f5:e9:78:d8:d2"
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"

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
print("\n--- dev.getCharacteristics() ----------------")
print(type(characteristics))
print(characteristics)

for char in characteristics:
	print("------------------")
	print(type(char))
	print(char.uuid)
	if char.uuid == CHARACTERISTIC_UUID:
		while True:
			print("=== !CHARACTERISTIC_UUID matched! ==")
			# nanoRP2040_Char = char
			# print(char)
			# print(dir(char))
			# print(char.getDescriptors)
			# print(char.propNames)
			# print(char.properties)
			# print(type(char.read()))
			# print("value length: ", len(char.read()))
			# packed_data = binascii.unhexlify(char.read

			s = struct.Struct("f f f")

			unpacked_data = s.unpack(char.read())
			print(unpacked_data)

			# print(unpacked_data)
			# val = struct.unpack("f", bytearray(char.read()))
			# print("Decoded value: ", val[0])
	


