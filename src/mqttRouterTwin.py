#===============================================================================
# mqttRouterTwin - Router for Twin State Cache Management
# Jon Durrant
# 10-Jan-2022
#===============================================================================
import logging
import paho.mqtt.client as mqtt
from mqttRouter import MQTTRouter 
import mqttTopicHelper as topicHelper
from twinState import TwinState
import twinProtocol
import json

class MQTTRouterTwin(MQTTRouter):
    def __init__(self, client_id: str):
        super().__init__(client_id)
        self.xLogging = logging.getLogger(__name__)
        
        self.xSet = topicHelper.getTwinSet("+")
        self.xGet = topicHelper.getTwinGet("+")
        
        self.xLC = topicHelper.genLifeCycleTopic("+", "#")
        self.xUpdate = topicHelper.getThingUpdate("+")
        
        self.xCache = {}
        
       
    def subscribe(self, interface: mqtt):
        interface.subscribe(self.xGet, qos=1)
        interface.subscribe(self.xSet, qos=1)
        interface.subscribe(self.xLC, qos=1)
        interface.subscribe(self.xUpdate, qos=1)
        
        
    def route(self, topic: str, payload: str, interface: mqtt):
        if ( topicHelper.topicEquals(self.xGet, topic)):
            target = self.tngTarget(topic)
            self.xLogging.debug("TODO Get %s"%topic)
            return True
        if ( topicHelper.topicEquals(self.xSet, topic)):
            target = self.tngTarget(topic)
            self.xLogging.debug("TODO Set %s"%topic)
            return True
        
        if ( topicHelper.topicEquals(self.xLC, topic)):
            target = self.tngTarget(topic)
            
            self.xLogging.debug("LC event on %s"%target)
            return True
            
        if (topicHelper.topicEquals(self.xUpdate, topic)):
            target = self.tngTarget(topic)
            
            self.xLogging.debug("Update on %s"%target)
            
            
            return True
        
        return False
        

    def tngTarget(self, topic: str):
        target = topic.split("/")[1]
        if (not target in self.xCache):
            self.xCache[target] = {}
            self.xLogging.debug("Added to Cache %s"%target)
        return target
    
    