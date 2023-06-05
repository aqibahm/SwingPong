from time import sleep
from threading import Thread

def some_task():
    while True:
        print("Task Running!")

t  = Thread(target = some_task)

t.daemon = True



snooziness = int(input("Enter the amount of seconds you want to run this: > "))
t.start()
sleep(snooziness)