from bluepy import btle
import time
import struct
import binascii
import pyrebase

# Have to match with peripheral:

# MAC = "ee:7a:ec:0e:56:67"
MAC = "c4:55:83:21:7c:a5"
SERVICE_UUID = "1101"
CHARACTERISTIC_UUID = "2101"

config = {
	"apiKey": "AlzaSyC97fthUcEVEYEqu5kkKdAHSh-22ucqsHs",
	"authDomain": "swingpong-28eda.firebaseapp.com",
	"databaseURL": "https://swingpong-28eda-default-rtdb.firebaseio.com",
	"storageBucket": "swingpong-28eda.appspot.com" 
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

print("Firebase Connection Successful!")

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
			# print("=== !CHARACTERISTIC_UUID matched! ==")
			# nanoRP2040_Char = char
			# print(char)
			# print(dir(char))
			# print(char.getDescriptors)
			# print(char.propNames)
			# print(char.properties)
			# print(type(char.read()))
			# print("value length: ", len(char.read()))
			# packed_data = binascii.unhexlify(char.read

			# s = struct.Struct("f f f")

			swing = int.from_bytes(char.read(), "big")
			
			if swing == 0:
				db.child("swingpong_pi_terminal").child("Player_1_Swings").push("Backhand")
				print("Backhand")
			elif swing == 1:
				db.child("swingpong_pi_terminal").child("Player_1_Swings").push("Forehand")
				print("Forehand")

			# print(unpacked_data)
			# val = struct.unpack("f", bytearray(char.read()))
			# print("Decoded value: ", val[0])
	


