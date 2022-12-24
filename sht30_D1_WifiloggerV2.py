import machine
from machine import I2C, Pin
import network

import utime as time
import ujson as json
import sht30
import umqtt.simple as umqtt
import ubinascii
import micropython
import gc

from machine import UART
uart=UART(0,115200)       #to enable keyboard breakin for debugging

mqtt_sensorId='4'
mqtt_clientId = ubinascii.hexlify(machine.unique_id())
mqtt_payload = {'measure':'tmp', 'value':1.23}
msg_id=0

sensor = sht30.SHT30()
#print(sensor.is_present())
#print(sensor.measure())
print("sensor initialized")
TEMPERATURE_BIAS = 0
HUMIDITY_BIAS = 0
SERVER = '192.168.1.101'  
time_of_last_xmit = 0

def deep_sleep(msecs):
    #configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    # set RTC.ALARM0 to fire after Xmilliseconds, waking the device
    rtc.alarm(rtc.ALARM0, msecs)
    #put the device to sleep
    machine.deepsleep()
    
def callback(topic, msg, retained):
    #print((topic, msg, retained))
    pass

def publish_reading(payload, measure):
    global client
    mqtt_msg = json.dumps(mqtt_payload)
    topic_str = 'home/sensor'+ mqtt_sensorId +'/'+measure
    print("publishing", topic_str, mqtt_msg)
    client.publish(topic=topic_str, msg=mqtt_msg)

def report(sensor):
    global time_of_last_xmit, mqtt_payload, msg_id, mqtt_client
    #print("get sensor data...")
    try:
        checkWlan()
        temperature, humidity = sensor.measure()
        #print("got it, formatting...")
        mqtt_payload['measure'] = 'tmp'
        mqtt_payload['value'] = temperature - TEMPERATURE_BIAS
        publish_reading(mqtt_payload, 'tmp')
        msg_id+=1

        mqtt_payload['measure'] = 'hum'
        mqtt_payload['value'] = humidity - HUMIDITY_BIAS
        publish_reading(mqtt_payload, 'hum')
        msg_id+=1
        return
    except Exception as e: #attempt to fetch and report measurements failed
        print(str(e))

def checkWlan():
    global wlan
    wlan = network.WLAN(network.STA_IF);
    while not wlan.isconnected():
        try:
            wlan.connect()
        except:
            pass
client = umqtt.MQTTClient(mqtt_clientId, SERVER, user='envSensor', password='1947nw')
client.set_callback(callback)
client.connect()

gc.collect()

from machine import WDT
wdt = WDT()

def main(event):
    global sensor, time_of_last_xmit, wdt
    try:
        time.sleep(1)
        if uart.any() > 0:
            machine.reset()       # should reset watchdog?
        print("reporting")
        report(sensor)
        print("reported")
    except Exception as e:
        machine.reset()
        print(e)
    except OSError as e:
        raise e
    print("deep sleeping")
    deep_sleep(10000)
 
main(0)
#RTC().wakeup(10000, main)
