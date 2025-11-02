import time
import board
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)
def delay(ms):
    time.sleep(ms/1000)
kbd.send(Keycode.GUI)
layout.write("cmd")
delay(100)
kbd.send(Keycode.ENTER)
delay(1500)
layout.write("systeminfo | findstr /I OS")
delay(100)
kbd.send(Keycode.ENTER)