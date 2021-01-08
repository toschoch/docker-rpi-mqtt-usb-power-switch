import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import time
from urllib.parse import urlparse
import logging
import subprocess

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

load_dotenv()

service_name = "mqtt-usb-power-switch"
device_name = os.environ['BALENA_DEVICE_NAME_AT_INIT']
mqtt_broker_address = urlparse(os.environ['MQTT_BROKER_ADDRESS'])
topic = "{}/usb/power/toggle".format(device_name)

# credentials
credentials = os.environ['MQTT_CREDENTIALS']
if os.path.isfile(credentials):
    with open(credentials, 'r') as fp:
        username, pw = fp.read().split(':')
else:
    username, pw = credentials.split(':')

cmd = ['uhubctl', '-l', '1-1', '-p 2', '-a']
#cmd = ['echo', 'value']

state_on = True


def switch_on():
    global state_on
    log.info("switch power on..")
    on_cmd = cmd + ['1']
    log.debug("send command: {}".format(' '.join(on_cmd)))
    ret = subprocess.check_output(on_cmd)
    log.debug("command returned: {}".format(ret))
    state_on = True


def switch_off():
    global state_on
    log.info("switch power off..")
    off_cmd = cmd + ['0']
    log.debug("send command: {}".format(' '.join(off_cmd)))
    ret = subprocess.check_output(off_cmd)
    log.debug("command returned: {}".format(ret))
    state_on = False


# Create client
client = mqtt.Client(client_id="{}/{}".format(device_name, service_name))
client.username_pw_set(username, pw)
client.enable_logger()


def subscribe(client, userdata, flags, rc):
    client.subscribe(topic)


def publish_on(client, userdata, flags, rc):
    client.publish(topic, payload=1)


# Function to process received message
def process_message(client, userdata, message):
    global state_on
    log.debug("message received {}".format(str(message.payload.decode("utf-8"))))
    log.debug("message topic={}".format(message.topic))
    log.debug("message qos={}".format(message.qos))
    log.debug("message retain flag={}".format(message.retain))
    requested_state = int(message.payload.decode("utf-8"))
    if requested_state:
        switch_on()
    else:
        switch_off()


# Assign callback function
client.reconnect_delay_set(min_delay=1, max_delay=120)
client.on_message = process_message
client.on_connect = subscribe
#client.on_subscribe = publish_on

client.connect(mqtt_broker_address.hostname,
               mqtt_broker_address.port, 60)

# Run loop
client.loop_forever()
client.disconnect()