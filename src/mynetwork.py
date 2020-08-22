import network
import secrets
def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(secrets.SSID, secrets.PW)
        while not sta_if.isconnected():	
            pass
        print('network config:', sta_if.ifconfig())
