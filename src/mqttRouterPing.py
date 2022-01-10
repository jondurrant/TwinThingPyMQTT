#===============================================================================
# mqttRouterPing - Router for Ping Messages
# Jon Durrant
# 10-Jan-2022
#===============================================================================
import logging
import paho.mqtt.client as mqtt
from mqttRouter import MQTTRouter 
import mqttTopicHelper as topicHelper

class MQTTRouterPing(MQTTRouter):
    def __init__(self, client_id: str):
        super().__init__(client_id)
        self.xLogging = logging.getLogger(__name__)
        self.xPing = topicHelper.genThingTopic(self.getClientId(), topicHelper.MQTT_TOPIC_PING)
        self.xPong = topicHelper.genThingTopic(self.getClientId(), topicHelper.MQTT_TOPIC_PONG)
        self.xGrpPing = topicHelper.genGroupTopic(topicHelper.MQTT_GRP_ALL, topicHelper.MQTT_TOPIC_PING )
        #self.xGrpPong = topicHelper.genGroupTopic(topicHelper.MQTT_GRP_ALL, topicHelper.MQTT_TOPIC_PONG )
        
    def subscribe(self, interface: mqtt):
        interface.subscribe(self.xPing, qos=1)
        interface.subscribe(self.xGrpPing, qos=1)
        
        
    def route(self, topic: str, payload: str, interface: mqtt):
        if ((topic == self.xPing) or (topic == self.xGrpPing)):
            interface.publish(self.xPong, payload, retain=False, qos=1)
            self.xLogging.debug("Sucessfully Routed %s"%topic)
            return True
        else:
            return False
        
