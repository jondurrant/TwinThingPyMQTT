#===============================================================================
# MQTT Agent - Manage connection and routing of messages with MQTT Hub
#===============================================================================

import paho.mqtt.client as mqtt
import json
import time
import logging
import mqttTopicHelper as topicHelper
from mqttObserver import MQTTObserver
from mqttRouter import MQTTRouter

#===============================================================================
# MQTT Agent Class
#===============================================================================
class MQTTAgent(mqtt.Client):
    
    #===========================================================================
    # Constructor
    #===========================================================================
    def __init__(self, client_id):
        super().__init__(client_id)
        self.xMqttUser = ""
        self.xMqttPwd = ""
        self.xDiconnectedTopic=""
        self.xConnectedTopic=""
        self.xMqttTarget = ""
        self.xMqttPort = 1883
        self.xReconnect = False
        self.xLogging = logging.getLogger(__name__)
        self.xObservers = []
        self.xRouters = []
        
        self.xDiconnectedTopic = topicHelper.genLifeCycleTopic(
            client_id, topicHelper.MQTT_TOPIC_LIFECYCLE_OFFLINE)
        self.xConnectedTopic = topicHelper.genLifeCycleTopic(
            client_id, topicHelper.MQTT_TOPIC_LIFECYCLE_ONLINE)

        
    #===========================================================================
    # Define credentials
    #===========================================================================
    def credentials(self, mqttUser : str, mqttPwd : str):
        self.xMqttUser = mqttUser
        self.xMqttPwd = mqttPwd
        
    
    def mqttHub(self, mqttTarget: str, mqttPort: int, recon: bool):
        self.xMqttTarget = mqttTarget
        self.xMqttPort = mqttPort
        self.xReconnect = recon
        self.username_pw_set(username=self.xMqttUser, password=self.xMqttUser)
        #self.start()
        
    def start(self):
        self.doConnect()
        
        #self.client.loop_start()
        self.loop_forever()
     
    def doConnect(self):
        j = {'online':0}
        p = json.dumps(j)
        self.will_set(self.xDiconnectedTopic, p, qos=1, retain=False) #set will  
        self.connect(self.xMqttTarget, self.xMqttPort, 60)
        
        j = {'online':1}
        p = json.dumps(j)
        infot = self.publish(self.xConnectedTopic,p,retain=False,qos=1)
        #infot.wait_for_publish()
            
    
    def on_connect(self, mqttc, obj, flags, rc):
        self.xLogging.debug("Connected")
        for o in self.xObservers:
            o.online()
        for r in self.xRouters:
            r.subscribe(self)
        return
    
    def on_message(self, mqttc, obj, msg):
        self.xLogging.debug("Received topic %s payload %s"%(msg.topic, str(msg.payload)))
        for o in self.xObservers:
            o.received()
        for r in self.xRouters:
            if (r.route(msg.topic, msg.payload, self)):
                return
        
    def on_disconnect(self, client, userdata, rc):
        self.xLogging.debug("Disconnected %d"%rc)
        for o in self.xObservers:
            o.offline()
        if (rc != 0):
            if (self.xReconnect):
                self.doConnect()
            
    def on_publish(self, client, userdata, mid):
        for o in self.xObservers:
            o.sent()
    
    def addObserver(self, o: MQTTObserver):
        self.xObservers.append(o)    
    
    def addRouter(self, router: MQTTRouter):
        self.xRouters.append(router)
    