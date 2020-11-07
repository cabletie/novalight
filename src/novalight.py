# Novalight as ported to micropython by @cabletie
# Running on TTGO T-Display and ESP32 DEV KIT V2 running Micropython 1.13
# Also conected to Adafruit RTC PCF8523 on pins 21,22 SDA,SCL respectively.
# Adafruit NeoPixel Ring x2 on 25,26 and NeoPixel Jewel7 on 27
# Original code by Charlyn https://charlyn.codes/ac-nova-light-clock/
# main.py
import random
from machine import * # Pin, I2C, RTC, WDT
import neopixel as np
import lib.urtc as urtc
import ntptime
import network
import utime
import math
import urequests as requests
import json

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
TZ = +11
TZ_SECONDS = TZ * 60 * 60
rtc = RTC()
is_it_friday = True
days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Error")

# Breathe stuff
smoothness_pts = 256 # larger=slower change in brightness
gamma = 0.11 # affects the width of peak (more or less darkness)
beta = 0.5 # shifts the gaussian to be symmetric

# This is set up and connected in the setup.py that shoud be called
# before this.
net_if = network.WLAN(network.STA_IF)

if True:   # change to True if you want to write the time!
    # Set machine.RTC and hw rtc to NTP time if available
    if net_if.isconnected():
        print("Getting timezone from timezone server")
        res = requests.get(url='http://api.timezonedb.com/v2.1/get-time-zone?key=F4XA80XV2770&format=json&by=zone&zone=Australia/Melbourne').text
        TZ_SECONDS = json.loads(res).get('gmtOffset')
        print('TZ_SECONDS: ',TZ_SECONDS)
        print("Getting time from NTP server")
        # Create an epoch based seconds time with retrieved time + TZ offset
        t = ntptime.time()+TZ_SECONDS
        # Convert it to a tuple
        utm = utime.localtime(t)
        # Set machine RTC with the new time
        rtc.datetime((utm[0],utm[1],utm[2],utm[6],utm[3],utm[4],utm[5],0))
        # Get current time from machine RTC
        tm = rtc.datetime()
        # And use it to set Battery Backed RTC
        hw_clock.datetime(tm)
    else:
        # No network, Get time from battery backed RTC
        dtt = hw_clock.datetime() 
        # And set machine RTC from it
        print(dtt)
        rtc.datetime((dtt.year, dtt.month, dtt.day, dtt.weekday, dtt.hour, dtt.minute, dtt.second, 0))

    # Print the time we ended up with
    print(rtc.datetime())

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

def breathe2(light_unit, color):
    global smoothness_pts# larger=slower change in brightness  
    global gamma # affects the width of peak (more or less darkness)
    global beta # shifts the gaussian to be symmetric
    color_arr = color

    for ii in range(smoothness_pts):
        # Uncomment one of Linear, Circular or Gaussian to your liking
        # Linear
        # brightness_val = 1.0 - math.fabs((2.0*(ii/smoothness_pts)) - 1.0)
        # Circular
        # brightness_val = math.sqrt(1.0 -  math.pow(math.fabs((2.0*(ii/smoothness_pts))-1.0),2.0))
        # Gaussian
        brightness_val = (math.exp(-(math.pow(((ii/smoothness_pts)-beta)/gamma,2.0))/2.0))

        multiplied_val = [int(element * brightness_val) for element in color_arr]
        light_unit.fill(multiplied_val)
        utime.sleep(.02)
        light_unit.write()

# For later - do breathe in the background or maybe via uasyncio
def breathecb(timer):
    global ii, smoothness_pts, gamma, beta, color_arr, breathe_en, star_frag

    if not breathe_en:
        return

    # Gaussian
    brightness_val = (math.exp(-(math.pow(((ii/smoothness_pts)-beta)/gamma,2.0))/2.0))

    multiplied_val = [int(element * brightness_val) for element in color_arr]
    star_frag.fill(multiplied_val)
    star_frag.write()
    if ii >= smoothness_pts:
        ii = 0
    else:
        ii += 1

def color_chase(light_unit, color, wait):
    for i in range(light_unit.n):
        light_unit[i] = color
        utime.sleep(wait)
        light_unit.write()
    # utime.sleep(0.5)

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
    color_chase(light_three, color3+(0,), wait)

def the_time_is_now(color, friday):
    if not friday:
        breathe2(star_frag, WHITE_RGBW)
        solid(top_nova, color)
        top_nova.write()

def it_feels_like(color):
    solid(bottom_nova, color)
    bottom_nova.write()

def friday_feels():
    wait = 0.05
    what_even_is_time(bottom_nova, top_nova, star_frag, wait)

# enable WDT with a timeout of 10s
# This gives enough time for the inline colour chases to work
wdt = WDT(timeout=10000)  

# Get time from our RTC
rdt = rtc.datetime()
tm = urtc.datetime_tuple(*rdt)
print("The date is %s %d/%d/%d" % (days[tm.weekday], tm.day, tm.month, tm.year))
print("The time is %d:%02d:%02d" % (tm.hour, tm.minute, tm.second))

start = 0
while True:
    # Feed the watchdog 
    # (I always thought you patted or kicked the watchdog, 
    # but apparently in Python, you feed it)
    # Next two lines for debugging how long between feeds
    # delta = utime.ticks_diff(utime.ticks_ms(), start) # compute time difference
    # start = utime.ticks_ms() # get millisecond counter
    wdt.feed()

    # Get time from our RTC
    rdt = rtc.datetime()
    tm = urtc.datetime_tuple(*rdt)

    if tm.weekday == 4:
        is_it_friday = True
    else:
        is_it_friday = False

    if tm.hour >= 0 and tm.hour < 7: # 12a to 7a, you should be sleeping
        allOff()
        utime.sleep(1)
        continue

    # Top nova light indicates time span
    if tm.minute == 0 and (tm.second >= 0 and tm.second < 10): # top of the hour party cuckoo rainbow
        wdt.feed()
        rainbow_chase(top_nova, 0.1)
        wdt.feed()
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
    # is_it_friday = False
    if days[tm.weekday] == "Sunday" or days[tm.weekday] == "Saturday":
        it_feels_like(WHITE)
    elif days[tm.weekday] == "Monday":
        it_feels_like(BLUE)
    elif days[tm.weekday] == "Tuesday":
        it_feels_like(CYAN)
    elif days[tm.weekday] == "Wednesday" or days[tm.weekday] == "Thursday":
        it_feels_like(PINK)
    elif days[tm.weekday] == "Friday":
        # is_it_friday = True
        friday_feels()
