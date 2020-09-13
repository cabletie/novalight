# Novalight ported to LoBo MicroPython by @cabletie
# main.py
import random
import machine
import lib.urtc
import lib.ntptime
import math

# import adafruit_pcf8523
# https://docs.micropython.org/en/latest/library/time.html
# try:
#     import utime as time
# except ImportError:
#     import time
import utime
import mynetwork

# LoBo Neopixel doco is at https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/wiki/neopixel

# COLORS
# OFF = (0, 0, 0)
# WHITE = (0, 0, 0, 255)
# WHITE_RGB = (100, 100, 100)

# RED = (100, 5, 5)
# BLUE = (0, 0, 100)
# GREEN = (50, 150, 50)
# PURPLE = (180,50,180)
# ORANGE = (155, 50, 0)
# YELLOW = (200, 150, 0)
# CYAN = (0, 100, 100)
# PINK = (231,84,128)

def pack(color):
    return color[0]<<16 | color[1]<<8 | color[2]

def unpack(color):
    return color & 0xff,(color>>8 & 0xff),(color >> 16 & 0xff)

OFF = pack((0, 0, 0))
ORANGE = pack((155, 50, 0))
PINK = pack((231, 84, 128))
PURPLE = machine.Neopixel.PURPLE
GREEN = machine.Neopixel.GREEN
YELLOW = machine.Neopixel.YELLOW
CYAN = machine.Neopixel.CYAN
WHITE = machine.Neopixel.WHITE
BLACK = machine.Neopixel.BLACK
RED = machine.Neopixel.RED
LIME = machine.Neopixel.LIME
BLUE = machine.Neopixel.BLUE
MAGENTA = machine.Neopixel.MAGENTA
SILVER = machine.Neopixel.SILVER
GRAY = machine.Neopixel.GRAY
MAROON = machine.Neopixel.MAROON
OLIVE = machine.Neopixel.OLIVE
TEAL = machine.Neopixel.TEAL
NAVY = machine.Neopixel.NAVY

color_array = [GREEN, PURPLE, ORANGE, YELLOW, CYAN, PINK, OFF, WHITE]

# Pixel numbers
STAR_FRAG_LEN = 7
TOP_NOVA_LEN = 16
BOTTOM_NOVA_LEN = 16

star_frag = machine.Neopixel(machine.Pin(27), STAR_FRAG_LEN, type=machine.Neopixel.TYPE_RGBW)
top_nova = machine.Neopixel(machine.Pin(25), TOP_NOVA_LEN, type=machine.Neopixel.TYPE_RGB)
bottom_nova = machine.Neopixel(machine.Pin(26), BOTTOM_NOVA_LEN, type=machine.Neopixel.TYPE_RGB)

# Start with eveything turned off
star_frag.clear()
star_frag.show()
top_nova.clear()
top_nova.show()
bottom_nova.clear()
bottom_nova.show()

# myI2C = machine.I2C(sda=machine.Pin(21), scl=machine.Pin(22))
# rtc = lib.urtc.PCF8523(myI2C)
# australia/melbourne
TZ = +10
TZ_SECONDS = TZ * 60 * 60
is_it_friday = True
days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Error")

# Connect to network to get NTP time
# mynetwork.do_connect()
if True:
    rtc = machine.RTC()
    rtc.ntp_sync(server="pool.ntp.org", tz="AEST-10AEDT,M10.1.0,M4.1.0/3")

if False:   # change to True if you want to write the time!
    t = lib.ntptime.time() # Get the time from the NTP server as seconds since epoch
    # Adjust for timezone (yes, we store localtime on the RTC ...)
    t += TZ_SECONDS
    # And convert to tuple
    tm = utime.localtime(t)

    ## uncomment for debugging
    # print("year, mon, date, hour, min, sec,  wday, doy")
    # print("NTP Time converted by utime.localtime(): ", tm, t)
    ## Adjust for day of week from 1-7 to 0-6
    # print("Write to RTC in this order: ", tm[0], tm[1], tm[2], tm[6]-1, tm[3], tm[4], tm[5], 0)
    rtc.datetime((tm[0], tm[1], tm[2], tm[6]-1, tm[3], tm[4], tm[5], 0))


def solid(light_unit, length, color):
    for i in range(length):
        light_unit.set(i+1, color)

def breathe(light_unit, length, color):
    smoothness_pts = 256 # larger=slower change in brightness  
    gamma = 0.11 # affects the width of peak (more or less darkness)
    beta = 0.5 # shifts the gaussian to be symmetric
    color_arr = unpack(color)

    for ii in range(smoothness_pts):
        # Linear
        # brightness_val = 1.0 - math.fabs((2.0*(ii/smoothness_pts)) - 1.0)
        # Circular
        # brightness_val = math.sqrt(1.0 -  math.pow(math.fabs((2.0*(ii/smoothness_pts))-1.0),2.0))
        # Gaussian
        brightness_val = (math.exp(-(math.pow(((ii/smoothness_pts)-beta)/gamma,2.0))/2.0))

        multiplied_val = [int(element * brightness_val) for element in color_arr]
        light_unit.set(1, pack(multiplied_val), num=STAR_FRAG_LEN)
        utime.sleep(.02)
        # light_unit.show()

def color_chase(light_unit, light_len, color, wait):
    for i in range(light_len):
        light_unit.set(i+1, color)
        utime.sleep(wait)
        light_unit.show()
    utime.sleep(0.5)

# BLACK, WHITE, RED, LIME, BLUE, YELLOW, CYAN, MAGENTA, SILVER, GRAY, MAROON, OLIVE, GREEN, PURPLE, TEAL, NAVY
def rainbow_chase(light_unit, length, wait):
    color_chase(light_unit, length, YELLOW, wait)
    color_chase(light_unit, length, GREEN, wait)
    color_chase(light_unit, length, RED, wait)  # Increase the number to slow down the color chase
    color_chase(light_unit, length, CYAN, wait)
    color_chase(light_unit, length, BLUE, wait)
    color_chase(light_unit, length, PURPLE, wait)

def pick_rando_color():
    pick = random.randint(0, (len(color_array)-1))
    rando_color = color_array[pick]
    return rando_color

def what_even_is_time(light_one, light_two, light_len, wait):
    color1 = pick_rando_color()
    color2 = pick_rando_color()
    color3 = pick_rando_color()
    if color1 == color2 == color3:
        color1 = pick_rando_color()

    color_chase(light_one, light_len, color1, wait)
    color_chase(light_two, light_len, color2, wait)
    color_chase(star_frag, STAR_FRAG_LEN, color3, wait)

def the_time_is_now(color, friday):
    if not friday:
        breathe(star_frag, STAR_FRAG_LEN, WHITE)
        top_nova.set(1, color, num=TOP_NOVA_LEN)

def it_feels_like(color):
    bottom_nova.set(1, color, num=BOTTOM_NOVA_LEN)
    # bottom_nova.show()

def friday_feels():
    wait = 0.05
    what_even_is_time(bottom_nova, top_nova, BOTTOM_NOVA_LEN, wait)

import ucollections

DateTimeTuple = ucollections.namedtuple("DateTimeTuple", ["year", "month",
    "day", "hour", "minute", "second", "weekday", "doy"])

def datetime_tuple(year, month, day, hour=0, minute=0,
                   second=0, weekday=0, doy=0):
    return DateTimeTuple(year, month, day, hour, minute,
                         second, weekday-1, doy)
while True:
    # Get time from our RTC
    tm = datetime_tuple(*utime.localtime())

    ## Uncomment for debugging
    print("Year: ",tm.year)
    print("Month:", tm.month)
    print("Day:", tm.day)
    print("Weekday:", tm.weekday)
    print("Hour:", tm.hour)
    print("Minute:", tm.minute)
    print("Second:", tm.second)
    if tm.weekday == 5:
        is_it_friday = True
    else:
        is_it_friday = False

    print("The date is %s %d/%d/%d" % (days[tm.weekday], tm.day, tm.month, tm.year))
    print("The time is %d:%02d:%02d" % (tm.hour, tm.minute, tm.second))

    if tm.hour >= 0 and tm.hour < 7: # 12a to 7a, you should be sleeping
        star_frag.clear()
        star_frag.show()
        top_nova.clear()
        top_nova.show()
        bottom_nova.clear()
        bottom_nova.show()
        continue

    # Top nova light indicates time span
    if tm.minute == 0 and (tm.second >= 0 and tm.second < 10): # top of the hour party cuckoo rainbow
        rainbow_chase(top_nova, TOP_NOVA_LEN, 0.1)
        rainbow_chase(top_nova, TOP_NOVA_LEN, 0.1)

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
