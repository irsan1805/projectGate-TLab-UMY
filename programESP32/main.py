from machine import Pin
from umqtt.simple import MQTTClient
import network
import time

# Initialize relay pins
relay1 = Pin(5, Pin.OUT)  # First relay (Open gate)
relay2 = Pin(18, Pin.OUT)  # Second relay (Close gate)

# Wi-Fi credentials
ssid = 'TLab Head Office'
password = 'mudabersemangat'

# MQTT server configuration
mqtt_broker = '172.254.3.114'  # Replace with your MQTT broker IP address
mqtt_port = 1884
mqtt_user = 'tlab'  # Replace with your MQTT username
mqtt_password = '1234'  # Replace with your MQTT password
mqtt_client_id = 'gate_controller1'
topic_open_forever = b'gate/open_forever'
topic_open = b'gate/open'
topic_close = b'gate/close'

# Connect to Wi-Fi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print('Connection successful')
print(station.ifconfig())

# Gate state variables
gate_open = False
open_forever = False

# Function to open the gate indefinitely
def open_gate_forever():
    global open_forever
    if not open_forever:
        relay1.value(1)  # Activate first relay to open gate
        relay2.value(0)  # Deactivate second relay (gate open state)
        open_forever = True
        print("Gate opened indefinitely")

# Function to open the gate temporarily
def open_gate():
    global gate_open, open_forever
    if not gate_open and not open_forever:
        relay1.value(1)  # Activate first relay to open gate
        relay2.value(0)  # Deactivate second relay (gate open state)
        gate_open = True
        print("Gate opened temporarily")
        # Start a timer to close the gate after 30 seconds
        time.sleep(5)
        close_gate()

# Function to close the gate
def close_gate():
    global gate_open, open_forever
    if gate_open or open_forever:
        relay1.value(0)  # Deactivate first relay (gate closed state)
        relay2.value(1)  # Activate second relay to close gate
        gate_open = False
        open_forever = False
        print("Gate closed")

# MQTT message callback function
def mqtt_callback(topic, msg):
    print(f"Received message: {msg} on topic: {topic}")
    if topic == topic_open:
        open_gate()
    elif topic == topic_close:
        close_gate()
    elif topic == topic_open_forever:
        open_gate_forever()

# Set up MQTT client
client = MQTTClient(mqtt_client_id, mqtt_broker, mqtt_port, mqtt_user, mqtt_password)

# Set the callback function to handle incoming messages
client.set_callback(mqtt_callback)

# Connect to MQTT broker and subscribe to topics
client.connect()
client.subscribe(topic_open, qos=1)
client.subscribe(topic_close, qos=1)
client.subscribe(topic_open_forever, qos=1)
print(f"Subscribed to {topic_open}, {topic_close}, and {topic_open_forever} with qos=1")

try:
    while True:
        client.check_msg()  # Wait for a message and process it if it arrives
        time.sleep(1)  # Check periodically

except KeyboardInterrupt:
    print("Disconnecting from MQTT...")
    client.disconnect()
    print("Disconnected")

