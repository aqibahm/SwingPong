import pyrebase
import time

config = {
	"apiKey": "AlzaSyC97fthUcEVEYEqu5kkKdAHSh-22ucqsHs",
	"authDomain": "swingpong-28eda.firebaseapp.com",
	"databaseURL": "https://swingpong-28eda-default-rtdb.firebaseio.com",
	"storageBucket": "swingpong-28eda.appspot.com" 

}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

print("Sending data to Firebase using Raspberry Pi")

while True:
	data = {"time": time.time()}
	db.child("pi4b").child("1-set").set(data)
	db.child("pi4b").child("2-push").push(data)


