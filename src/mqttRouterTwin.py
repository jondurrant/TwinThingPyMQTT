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
from twin import Twin
import twinProtocol
import json

class MQTTRouterTwin(MQTTRouter):
    def __init__(self, client_id: str):
        super().__init__(client_id)
        self.xLogging = logging.getLogger(__name__)
        
        self.xSet = topicHelper.getTwinSet("+")
        self.xGet = topicHelper.getTwinGet("+")
        
        self.xLC = topicHelper.genLifeCycleTopic("+", topicHelper.MQTT_TOPIC_LIFECYCLE_ONLINE)
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
        
        #THing Online Sequence
        if ( topicHelper.topicEquals(self.xLC, topic)):
            target = self.tngTarget(topic)
            if (not self.isNewTwin(target)):
                
                twin = self.getTwin(target)
                setTopic = topicHelper.getThingSet(target)
                setState = {'state': twin.getReportedState()}
                #setState = {'delta': twin.getReportedState()}
                self.xLogging.debug("Set state on returning thing %s state %s"%(target, json.dumps(setState,sort_keys=True, indent=4) ))
                interface.publish(setTopic, json.dumps(setState), retain=False, qos=1)
                
                if (not twin.isUptoDate()):
                    deltaState = {'delta': twin.getDelta()}
                    self.xLogging.debug("Set delta for returning thing %s delta %s"%(target, json.dumps(deltaState,sort_keys=True, indent=4)))
                    interface.publish(setTopic, json.dumps(deltaState), retain=False, qos=1)
            else:
                self.xLogging.debug("Unknown thing, so requesting get %s"%target)
                getTopic = topicHelper.getThingGet(target)
                interface.publish(getTopic, "{'GET': 1}", retain=False, qos=1)
                
            
            self.xLogging.debug("LC event on %s"%topic)
            return True
            
        #Habdle Update from Thing
        if (topicHelper.topicEquals(self.xUpdate, topic)):
            target = self.tngTarget(topic)
            n = self.isNewTwin(target)
            twin = self.getTwin(target)
            j = json.loads(payload)
            if ("delta" in j):
                twin.updateFromThing(j["delta"])
                if (n):
                    getTopic = topicHelper.getThingGet(target)
                    interface.publish(getTopic, "{'GET': 1}", retain=False, qos=1)
                
            elif ("state" in j):
                twin.stateFromThing(j["state"])
                #self.xLogging.debug("Twin %s state Payload %s"%(target, payload))
            
            self.xLogging.debug("Twin %s Reported %s"%(target, json.dumps(twin.getReportedState(), sort_keys=True, indent=4)))
            self.pubUpdated(target, twin, interface)
            return True
        
        return False
        

    def tngTarget(self, topic: str):
        target = topic.split("/")[1]
        
        return target
    
    def getTwin(self, target: str):
        if (not target in self.xCache):
            self.xCache[target] = Twin()
            self.xLogging.debug("Added to Cache %s"%target)
        return self.xCache[target]
      
    def isNewTwin(self, target: str):
        return (not target in self.xCache)
    
    def pubUpdated(self, target: str, twin: Twin, interface: mqtt):
        upd = { "desired": twin.getDesiredState(),
               "desiredMeta": twin.getDesiredMeta(),
               "reported": twin.getReportedState(),
               "reportedMeta": twin.getReportedMeta(),
               "declined": twin.getDeclinedState(),
               "declinedMeta": twin.getDeclinedMeta()
        }
        updTopic = topicHelper.getTwinUpdate(target)
        interface.publish(updTopic, json.dumps(upd), retain=False, qos=1)
            
            
    