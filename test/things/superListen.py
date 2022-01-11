import paho.mqtt.client as mqtt
import json
import time
import random

host = "nas3"
port = 1883
user = "super"
passwd = "test"

connected_topic = "TNG/" + user + "/LC/ON"
diconnected_topic = "TNG/" + user + "/LC/OFF"

tng_topics = "#"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Rcv topic=" +msg.topic+" msg="+str(msg.payload))
    

def on_disconnect():
    print("DISCONNNECTED")


client = mqtt.Client(client_id=user)
client.username_pw_set(username=user, password=passwd)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

j = {'online':0}
p = json.dumps(j)
client.will_set(diconnected_topic, p, qos=1, retain=False) #set will

client.connect(host, port, 60)

client.loop_start()

client.subscribe( tng_topics )
    
print("publishing connect")
j = {'online':1}
p = json.dumps(j)
client.publish(connected_topic,p,retain=False,qos=1)



time.sleep(200)