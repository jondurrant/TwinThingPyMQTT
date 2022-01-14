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
from twinObserver import TwinObserver
import twinProtocol
from mqttStateObserver import MQTTStateObserver
import json

class MQTTRouterState(MQTTRouter, TwinObserver):
    def __init__(self, client_id: str, state: TwinState, interface: mqtt):
        super().__init__(client_id)
        self.xLogging = logging.getLogger(__name__)
        self.xSet = topicHelper.getThingSet(self.getClientId())
        self.xGet = topicHelper.getThingGet(self.getClientId())
        self.xUpdate = topicHelper.getThingUpdate(self.getClientId())
        self.xState = state
        self.xState.attachObserver(self)
        self.interface = interface
        self.xObservers  = []
       
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
                d = self.setFilter(j[twinProtocol.TWINDELTA])
                self.xState.updateState(d)
                self.notifyObservers()
            if twinProtocol.TWINSTATE in j:
                if (self.deleteAllowed(topic, payload)):
                    self.xState.deleteState()
                d = self.setFilter(j[twinProtocol.TWINSTATE])
                self.xState.updateState(d)
                self.notifyObservers()
            self.sendUpdate(interface)
        
            self.xLogging.debug("Sucessfully Routed %s"%topic)
            return True
       
        return False
        

    def sendUpdate(self, interface: mqtt):
        res = {}
        res[twinProtocol.TWINSTATE] = self.xState.getState()
        s = json.dumps(res)
        interface.publish(self.xUpdate, s, retain=False, qos=1)
        
        
    def setFilter(self, delta: dict):
        return delta
    
    def deleteAllowed(self, topic: str, payload: str):
        return True
    
    def attachObserver(self, obs: MQTTStateObserver):
        self.xObservers.append(obs)
        
    def dettachObserver(self, obs: MQTTStateObserver):
        self.xObservers.remove(obs)    
        
    def notifyObservers(self):
        for obs in self.xObservers:
            obs.stateNotify(self.xState)  
            
            
    def updateState(self, delta: dict, interface: mqtt = None):
        self.xState.updateState(delta)
        self.notifyObservers()
        if (interface):
            self.sendUpdate(interface)
        
    def getState(self):
        return self.xState.getState()
    
    def notify(self):
        self.sendUpdate(self.interface)
    