import time
import board
import wifi
import socketpool
import ipaddress
import ssl
import digitalio
import usb_hid
import sys
import supervisor
import asyncio
from webapp import *
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

def connect_wifi():
    try:
        from secrets import secrets
    except ImportError:
        print('Can\'t find secrets.py')
        raise

    # print(f'Connecting to {secrets['ssid']}...', end='')
    # try:
    #     wifi.radio.set_ipv4_address(
    #         ipv4=ipaddress.IPv4Address("192.168.0.128"),
    #         netmask=ipaddress.IPv4Address("255.255.255.0"),
    #         gateway=ipaddress.IPv4Address("192.168.0.1"),
    #         ipv4_dns=ipaddress.IPv4Address("1.1.1.1")
    #     )
    #     wifi.radio.connect(secrets['ssid'], secrets['password'])
    try:
        print(f'Starting wifi with ssid: {secrets['ssid']}...', end='')
        wifi.radio.start_ap(secrets['ssid'],secrets['password'])
        print("Succeed.")
        HOST = repr(wifi.radio.ipv4_address_ap)
        PORT = 80        # Port to listen on
        print(HOST,PORT)
    except Exception as e:
        print(f' Failed.\nError occured: {e}')
        sys.exit()

    # print(f" Succeed.\nNow connected to {secrets['ssid']}")
    # print(f"IP Addr: {wifi.radio.ipv4_address}\nGateway: {wifi.radio.ipv4_gateway}")

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

led = digitalio.DigitalInOut(board.LED)
led.switch_to_output()

async def blink_pico_w_led(led):
    print("starting blink_pico_w_led")
    led_state = False
    while True:
        if led_state:
            #print("led on")
            led.value = 1
            await asyncio.sleep(0.5)
            led_state = False
        else:
            #print("led off")
            led.value = 0
            await asyncio.sleep(0.5)
            led_state = True
        await asyncio.sleep(0.5)

async def main_loop():
    global led

    pico_led_task = asyncio.create_task(blink_pico_w_led(led))
    print("Starting Wifi")
    connect_wifi()
    print("Starting Web Service")
    webservice_task = asyncio.create_task(start_web_service())
    await asyncio.gather(pico_led_task, webservice_task)

asyncio.run(main_loop())