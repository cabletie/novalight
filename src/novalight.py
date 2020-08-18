# Novalight ported to LoBo MicroPython by @cabletie
# main.py
import machine
import lib.urtc
# import adafruit_pcf8523
# https://docs.micropython.org/en/latest/library/utime.html
import utime
import urandom
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

brightness_val = 0.7
star_frag = machine.Neopixel(machine.Pin(27), STAR_FRAG_LEN, type=machine.Neopixel.TYPE_RGBW)
top_nova = machine.Neopixel(machine.Pin(26), TOP_NOVA_LEN, type=machine.Neopixel.TYPE_RGB)
bottom_nova = machine.Neopixel(machine.Pin(25), BOTTOM_NOVA_LEN, type=machine.Neopixel.TYPE_RGB)

# Start with eveything turned off
star_frag.clear()
star_frag.show()
top_nova.clear()
top_nova.show()
bottom_nova.clear()
bottom_nova.show()

myI2C = machine.I2C(sda=machine.Pin(21), scl=machine.Pin(22))
rtc = lib.urtc.PCF8523(myI2C)
is_it_friday = True
days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")

if True:   # change to True if you want to write the time!
    #                     year, mon, date, hour, wday, min, sec, msec
    t = lib.urtc.datetime_tuple(2020, 8, 17, 1, 21, 59, 50, 0)
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time

    print("Setting time to:", t)     # uncomment for debugging
    rtc.datetime(t)
    print()


def solid(light_unit, length, color):
    for i in range(1, length):
        light_unit.set(i, color)

def breathe(light_unit, length, color):
    for i in range(1, length):
        light_unit.set(i, color, update=False)
        utime.sleep(.07)
        light_unit.show()

    utime.sleep(1)

    for i in range(1, length):
        light_unit.set(i, OFF, update=False)
        utime.sleep(.07)
        light_unit.show()

def color_chase(light_unit, light_len, color, wait):
    for i in range(light_len):
        light_unit.set(i, color)
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
    pick = urandom.randint(0, (len(color_array)-1))
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
        # top_nova.fill(color)
        # top_nova.show()

def it_feels_like(color):
    bottom_nova.set(1, color, num=BOTTOM_NOVA_LEN)
    # bottom_nova.show()

def friday_feels():
    wait = 0.05
    what_even_is_time(bottom_nova, top_nova, BOTTOM_NOVA_LEN, wait)

oldseconds = 0

while True:
    t = rtc.datetime()
    if t.second == oldseconds:
        continue
    oldseconds = t.second
    print(t)     # uncomment for debugging

    print("The date is %s %d/%d/%d" % (days[t.weekday], t.day, t.month, t.year))
    print("The time is %d:%02d:%02d" % (t.hour, t.minute, t.second))

    if t.hour >= 0 and t.hour < 7: # 12a to 7a, you should be sleeping
        star_frag.clear()
        star_frag.show()
        top_nova.clear()
        top_nova.show()
        bottom_nova.clear()
        bottom_nova.show()
        continue

    # Top nova light indicates time span
    if t.minute == 0 and (t.second >= 0 and t.second < 10): # top of the hour party cuckoo rainbow
        rainbow_chase(top_nova, TOP_NOVA_LEN, 0.01)
        rainbow_chase(top_nova, TOP_NOVA_LEN, 0.01)

    if t.hour >= 0 and t.hour < 7: # 12a to 7a, you should be sleeping
        the_time_is_now(OFF, is_it_friday)
    elif t.hour >= 7 and t.hour < 12: # 7a to 12p rise and shine! it's morning!
        the_time_is_now(WHITE, is_it_friday) # newborn nova
    elif t.hour >= 12 and t.hour < 15: # 12p to 3p, middle of the day burns bright
        the_time_is_now(CYAN, is_it_friday)
    elif t.hour >= 15 and t.hour < 18: # 3p to 6p, back to whatever you were doing
        the_time_is_now(YELLOW, is_it_friday)
    elif t.hour >= 18 and t.hour < 23: # 6p to 11p, night time calm
        the_time_is_now(ORANGE, is_it_friday)
    elif t.hour >= 23 and t.hour < 24: # 11p - 12a, time for bed!
        print("Super Novaaaaaa!")
        the_time_is_now(RED, is_it_friday) # super novaaaa

    # Bottom nova light indicates day of week
    if days[t.weekday] == "Sunday" or days[t.weekday] == "Saturday":
        it_feels_like(WHITE)
        is_it_friday = False
    elif days[t.weekday] == "Monday":
        it_feels_like(BLUE)
    elif days[t.weekday] == "Tuesday":
        it_feels_like(CYAN)
    elif days[t.weekday] == "Wednesday" or days[t.weekday] == "Thursday":
        it_feels_like(PINK)
    elif days[t.weekday] == "Friday":
        is_it_friday = True
        friday_feels()
