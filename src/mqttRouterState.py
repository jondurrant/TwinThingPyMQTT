#===============================================================================
# mqttRouterState - Router for Twin State of a Thing
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

class MQTTRouterState(MQTTRouter):
    def __init__(self, client_id: str, state: TwinState):
        super().__init__(client_id)
        self.xLogging = logging.getLogger(__name__)
        self.xSet = topicHelper.getThingSet(self.getClientId())
        self.xGet = topicHelper.getThingGet(self.getClientId())
        self.xUpdate = topicHelper.getThingUpdate(self.getClientId())
        self.xState = state
       
    def subscribe(self, interface: mqtt):
        interface.subscribe(self.xGet, qos=1)
        interface.subscribe(self.xSet, qos=1)
        
        
    def route(self, topic: str, payload: str, interface: mqtt):
        if (topic == self.xGet):
            res = {}
            res[twinProtocol.TWINSTATE] = self.xState.getState()
            s = json.dumps(res)
            interface.publish(self.xUpdate, s, retain=False, qos=1)
            self.xLogging.debug("Sucessfully Routed %s"%topic)
            return True
        if (topic == self.xSet):
            j = json.loads(payload)
            if twinProtocol.TWINDELTA in j:
                self.xState.updateState(j[twinProtocol.TWINDELTA])
            if twinProtocol.TWINSTATE in j:
                self.xState.deleteState()
                self.xState.updateState(j[twinProtocol.TWINSTATE])
                
            self.sendUpdate(interface)
        
            self.xLogging.debug("Sucessfully Routed %s"%topic)
            return True
       
        return False
        

    def sendUpdate(self, interface: mqtt):
        res = {}
        res[twinProtocol.TWINSTATE] = self.xState.getState()
        s = json.dumps(res)
        interface.publish(self.xUpdate, s, retain=False, qos=1)