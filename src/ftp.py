# connect to a WIFI AP, sync time and start telnet and FTP server
# Paste it in the Python command line (REPL)
# Then you can connect to the IP of your ESP32 in FTP (passive mode) or in telnet !

# found in second field, text before the coma, in 
# https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/blob/master/MicroPython_BUILD/components/micropython/docs/zones.csv
my_timezone = "AEST-10AEDT,M10.1.0,M4.1.0/3"

import network
import machine
import time
import secrets as s

wifi_ssid = s.SSID
wifi_passwd = s.PW

sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
sta_if.connect(wifi_ssid, wifi_passwd)
print("Waiting to connect")
while not sta_if.isconnected():
  print(".",end="")
  time.sleep(1)
  pass
time.sleep(6)
sta_if.ifconfig()

rtc = machine.RTC()
rtc.init((2018, 01, 01, 12, 12, 12))
rtc.ntp_sync(server= "", tz=my_timezone, update_period=3600)
network.ftp.start(user="micro", password="python", buffsize=1024, timeout=300)
network.telnet.start(user="micro", password="python", timeout=300)
print("\nIP of this ESP32 is : " + sta_if.ifconfig()[0])