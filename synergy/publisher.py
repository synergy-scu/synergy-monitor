import paho.mqtt.publish as publish
 
MQTT_SERVER = '192.168.0.31'
MQTT_PATH = 'hub_channel'

def publish_data(data):
	# print(data)
	publish.single(MQTT_PATH, data, hostname=MQTT_SERVER)
	return
