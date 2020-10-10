from machine import *
import network
import secrets
import utime

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

sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect(secrets.SSID, secrets.PW)
    timeout = 0
    while not sta_if.isconnected() and (timeout < 100):
        utime.sleep(0.1)
        timeout += 1
    print('timeout:',timeout)
print('network config:', sta_if.ifconfig())

# uftpd is symlinked here from ~/Documents/SRC/FTP-Server-for-ESP8266-ESP32-and-PYBD/uftpd.p
# This starts FTP daemon with defaults
if(sta_if.isconnected()):
  import lib.uftpd as uftpd
else:
  print("No network - not starting FTP")