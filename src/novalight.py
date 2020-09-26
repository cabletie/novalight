# Novalight ported to LoBo MicroPython by @cabletie
# main.py
import random
from machine import Pin, I2C, RTC
# from machine import neopixel
import neopixel as np
# import machine
import lib.urtc
# import lib.ntptime
import ntptime
import network
import secrets
import utime

# import adafruit_pcf8523
# https://docs.micropython.org/en/latest/library/time.html
# try:
#     import utime as time
# except ImportError:
#     import time
# import mynetwork

# LoBo Neopixel doco is at https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/wiki/neopixel

# COLORS
OFF = (0, 0, 0)
WHITE_RGBW = (0, 0, 0, 255)
WHITE = (100, 100, 100)

RED = (100, 5, 5)
BLUE = (0, 0, 100)
GREEN = (50, 150, 50)
PURPLE = (180, 50, 180)
ORANGE = (155, 50, 0)
YELLOW = (200, 150, 0)
CYAN = (0, 100, 100)
PINK = (231, 84, 128)

def pack(color):
    return color[0]<<16 | color[1]<<8 | color[2]

# OFF = pack((0, 0, 0))
# ORANGE = pack((155, 50, 0))
# PINK = pack((231, 84, 128))
# PURPLE = machine.Neopixel.PURPLE
# GREEN = machine.Neopixel.GREEN
# YELLOW = machine.Neopixel.YELLOW
# CYAN = machine.Neopixel.CYAN
# WHITE = machine.Neopixel.WHITE
# BLACK = machine.Neopixel.BLACK
# RED = machine.Neopixel.RED
# LIME = machine.Neopixel.LIME
# BLUE = machine.Neopixel.BLUE
# MAGENTA = machine.Neopixel.MAGENTA
# SILVER = machine.Neopixel.SILVER
# GRAY = machine.Neopixel.GRAY
# MAROON = machine.Neopixel.MAROON
# OLIVE = machine.Neopixel.OLIVE
# TEAL = machine.Neopixel.TEAL
# NAVY = machine.Neopixel.NAVY

color_array = [GREEN, PURPLE, ORANGE, YELLOW, CYAN, PINK, OFF, WHITE]

# Pixel numbers
STAR_FRAG_LEN = 7
TOP_NOVA_LEN = 16
BOTTOM_NOVA_LEN = 16

brightness_val = 0.7
pin27 = Pin(27, Pin.OUT)
pin25 = Pin(25, Pin.OUT)
pin26 = Pin(26, Pin.OUT)

star_frag = np.NeoPixel(pin27, STAR_FRAG_LEN, bpp=4)
top_nova = np.NeoPixel(pin25, TOP_NOVA_LEN)
bottom_nova = np.NeoPixel(pin26, BOTTOM_NOVA_LEN)

# Start with eveything turned off
def allOff():
    star_frag.fill(OFF+(0,))
    star_frag.write()
    top_nova.fill(OFF)
    top_nova.write()
    bottom_nova.fill(OFF)
    bottom_nova.write()

allOff()

# Setup I2C for talking to the HW RTC chip
myI2C = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)
hw_clock = urtc.PCF8523(myI2C)
rtc = RTC.init(2020,1,1,0,0,0,0,)
TZ = +10
TZ_SECONDS = TZ * 60 * 60
is_it_friday = True
days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Error")

# Connect to network to get NTP time
def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(secrets.SSID, secrets.PW)
        timeout = 0
        while not sta_if.isconnected() & timeout < 50:
            utime.sleep(0.1)
            timeout += 1
            pass
        print('network config:', sta_if.ifconfig())
    return sta_if

net_if = do_connect()

if True:   # change to True if you want to write the time!
    # Set machine.RTC and hw rtc to NTP time if available
    if net_if.isconnected():
        ntptime.settime()

        hw_clock.datetime((tm[0]-30, tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
    else
        # Get time from hw rtc
        hw_clock.datetime()
    # t = lib.ntptime.time() # Get the time from the NTP server as seconds since epoch
    # Adjust for timezone (yes, we store localtime on the RTC ...)
    # t += TZ_SECONDS
    # And convert to tuple
    # tm = utime.localtime(t)

    ## uncomment for debugging
    print("year, mon, date, hour, min, sec,  wday, doy")
    print("NTP Time converted by utime.localtime(): ", tm, t)
    ## Adjust for day of week from 1-7 to 0-6
    print("Write to RTC in this order: ", tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0)
    # rtc.datetime((tm[0]-30, tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))


def solid(light_unit, color):
    for i in range(light_unit.n):
        light_unit[i] = color

def breathe(light_unit, color):
    print("breathing on", color)
    for i in range(light_unit.n):
        light_unit[i] = color
        utime.sleep(.07)
        light_unit.write()

    utime.sleep(1)

    print("breathing off", OFF+(0,))
    for i in range(light_unit.n):
        light_unit[i] = OFF+(0,)
        utime.sleep(.07)
        light_unit.write()

def color_chase(light_unit, color, wait):
    for i in range(light_unit.n):
        light_unit[i] = color
        utime.sleep(wait)
        light_unit.write()
    utime.sleep(0.5)

# BLACK, WHITE, RED, LIME, BLUE, YELLOW, CYAN, MAGENTA, SILVER, GRAY, MAROON, OLIVE, GREEN, PURPLE, TEAL, NAVY
def rainbow_chase(light_unit, wait):
    color_chase(light_unit, YELLOW, wait)
    color_chase(light_unit, GREEN, wait)
    color_chase(light_unit, RED, wait)  # Increase the number to slow down the color chase
    color_chase(light_unit, CYAN, wait)
    color_chase(light_unit, BLUE, wait)
    color_chase(light_unit, PURPLE, wait)

def pick_rando_color():
    pick = random.randint(0, (len(color_array)-1))
    rando_color = color_array[pick]
    return rando_color

def what_even_is_time(light_one, light_two, light_three, wait):
    color1 = pick_rando_color()
    color2 = pick_rando_color()
    color3 = pick_rando_color()
    if color1 == color2 == color3:
        color1 = pick_rando_color()

    color_chase(light_one, color1, wait)
    color_chase(light_two, color2, wait)
    color_chase(light_three, color3, wait)

def the_time_is_now(color, friday):
    if not friday:
        breathe(star_frag, WHITE_RGBW)
        solid(top_nova, color)
        top_nova.write()

def it_feels_like(color):
    solid(bottom_nova, color)
    bottom_nova.write()

def friday_feels():
    wait = 0.05
    what_even_is_time(bottom_nova, top_nova, star_frag, wait)

while True:
    # Get time from our RTC
    tm = rtc.datetime()

    ## Uncomment for debugging
    # print("Year: ",tm.year)
    # print("Month:", tm.month)
    # print("Day:", tm.day)
    # print("Weekday:", tm.weekday)
    # print("Hour:", tm.hour)
    # print("Minute:", tm.minute)
    # print("Second:", tm.second)
    if tm.weekday == 5:
        is_it_friday = True
    else:
        is_it_friday = False

    print("The date is %s %d/%d/%d" % (days[tm.weekday], tm.day, tm.month, tm.year))
    print("The time is %d:%02d:%02d" % (tm.hour, tm.minute, tm.second))

    if tm.hour >= 0 and tm.hour < 7: # 12a to 7a, you should be sleeping
        allOff()
        continue

    # Top nova light indicates time span
    if tm.minute == 0 and (tm.second >= 0 and tm.second < 10): # top of the hour party cuckoo rainbow
        rainbow_chase(top_nova, 0.1)
        rainbow_chase(top_nova, 0.1)

    if tm.hour >= 0 and tm.hour < 7: # 12a to 7a, you should be sleeping
        the_time_is_now(OFF, is_it_friday)
    elif tm.hour >= 7 and tm.hour < 12: # 7a to 12p rise and shine! it's morning!
        the_time_is_now(WHITE, is_it_friday) # newborn nova
    elif tm.hour >= 12 and tm.hour < 15: # 12p to 3p, middle of the day burns bright
        the_time_is_now(CYAN, is_it_friday)
    elif tm.hour >= 15 and tm.hour < 18: # 3p to 6p, back to whatever you were doing
        the_time_is_now(YELLOW, is_it_friday)
    elif tm.hour >= 18 and tm.hour < 23: # 6p to 11p, night time calm
        the_time_is_now(ORANGE, is_it_friday)
    elif tm.hour >= 23 and tm.hour < 24: # 11p - 12a, time for bed!
        the_time_is_now(RED, is_it_friday) # super novaaaa

    # Bottom nova light indicates day of week
    if days[tm.weekday] == "Sunday" or days[tm.weekday] == "Saturday":
        it_feels_like(WHITE)
        is_it_friday = False
    elif days[tm.weekday] == "Monday":
        it_feels_like(BLUE)
    elif days[tm.weekday] == "Tuesday":
        it_feels_like(CYAN)
    elif days[tm.weekday] == "Wednesday" or days[tm.weekday] == "Thursday":
        it_feels_like(PINK)
    elif days[tm.weekday] == "Friday":
        is_it_friday = True
        friday_feels()
