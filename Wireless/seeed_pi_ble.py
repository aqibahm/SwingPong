import sys
import time
from argparse import ArgumentParser
from struct import *
import binascii

from bluepy import btle  # linux only (no mac)


# BLE IoT Sensor Demo
# Author: Gary Stafford
# Reference: https://elinux.org/RPi_Bluetooth_LE
# Requirements: python3 -m pip install –user -r requirements.txt
# To Run: python3 ./rasppi_ble_receiver.py d1:aa:89:0c:ee:82 <- MAC address – change me!


def main():
    # get args
    args = get_args()

    print("Connecting…")
    nano_sense = btle.Peripheral(args.mac_address)

    print("Discovering Services…")
    _ = nano_sense.services
    imu_sensing_service = nano_sense.getServiceByUUID("19B10000-E8F2-537E-4F6C-D104768A1214")

    print("Discovering Characteristics…")
    _ = imu_sensing_service.getCharacteristics()

    while True:
        print("\n")
        read_seeed(imu_sensing_service)
        # time.sleep(2) # transmission frequency set on IoT device


def byte_array_to_int(value):
    # Raw data is hexstring of int values, as a series of bytes, in little endian byte order
    # values are converted from bytes -> bytearray -> int
    # e.g., b'\xb8\x08\x00\x00' -> bytearray(b'\xb8\x08\x00\x00') -> 2232

    # print(f"{sys._getframe().f_code.co_name}: {value}")

    value = bytearray(value)
    value = int.from_bytes(value, byteorder="little")
    return value

def byte_array_to_float(value):
    value = bytearray(value)
    value = float.from_bytes(value, byteorder="little")
    return value


def byte_array_to_char(value):
    # e.g., b'2660,2058,1787,4097\x00' -> 2659,2058,1785,4097
    value = value.decode("utf-8")
    return value


def decimal_exponent_two(value):
    # e.g., 2350 -> 23.5
    return value / 100


def decimal_exponent_one(value):
    # e.g., 988343 -> 98834.3
    return value / 10


def pascals_to_kilopascals(value):
    # 1 Kilopascal (kPa) is equal to 1000 pascals (Pa)
    # to convert kPa to pascal, multiply the kPa value by 1000
    # 98834.3 -> 98.8343
    return value / 1000


def celsius_to_fahrenheit(value):
    return (value * 1.8) + 32


def read_seeed(service):
    imu_char = service.getCharacteristics("19B10001-E8F2-537E-4F6C-D104768A1214")[0]
    if imu_char.supportsRead():
        while 1:
            val = imu_char.read()
            print(val)

def get_args():
    arg_parser = ArgumentParser(description="BLE IoT Sensor Demo")
    arg_parser.add_argument('mac_address', help="MAC address of device to connect")
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
