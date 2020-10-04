import lib.urtc as urtc
# from machine import I2C, Pin, RTC
from machine import *
myI2C = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)
hw_clock = urtc.PCF8523(myI2C)
rtc = RTC()
def reason(r):
  switcher = {
    PWRON_RESET: 'Power on Reset',
    HARD_RESET: 'Hard Reset',
    WDT_RESET: 'WDT Reset',
    DEEPSLEEP_RESET: 'Deep sleep Reset',
    SOFT_RESET: 'soft Reset'
  }
  return switcher.get(r,'Unknown')
print(reason(reset_cause()))
