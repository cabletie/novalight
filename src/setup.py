import lib.urtc as urtc
from machine import I2C, Pin
from machine import RTC
myI2C = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)
hw_clock = urtc.PCF8523(myI2C)
rtc = RTC()
