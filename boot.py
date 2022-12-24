# This file is executed on every boot (including wake-boot from deepsleep)
import network
import time
import micropython
import secret
import machine

from machine import UART
uart=UART(0,115200)

time.sleep(3)
micropython.kbd_intr(ord('q')) # allow an interrupt before launching app
station = network.WLAN(network.STA_IF)
station.active(True)


while station.isconnected() == False:
    print ("connecting...")
    try:
        station.connect(secret.ssid, secret.password)
        micropython.kbd_intr(ord('q')) # allow an interrupt before launching app
        time.sleep(4)
        if uart.any() > 0: break
    except KeyboardInterrupt:
        machine.reset()
        pass
    except Exception as e:
        print(e)
        machine.reset()

print(station.ifconfig())
import ugit
try:
    cause=machine.reset_cause()
    print("reset_cause", cause)
    if cause==machine.WDT_RESET or cause==machine.PWRON_RESET:
        ugit.pull_all(isconnected=True)
    micropython.kbd_intr(ord('q')) # allow an interrupt before launching app
    for i in range(5):
        print("waiting", (5-i), "secs")
        if uart.any() > 0:
            machine.reset()
            break
        time.sleep(1)
    import sht30_D1_WifiloggerV2
except KeyboardInterrupt:
    machine.reset()


