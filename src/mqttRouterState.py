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
    #===========================================================================
    # Constructor:
    # client_id: str - client id of the thing
    # state: TwinState - state that this thing will manage
    # interface: mqtt - Interface to mqtt needed so it can publish an update on
    # a state change
    #===========================================================================
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
       
    #===========================================================================
    # Suscribe to the Get and Set topics for the thing
    #===========================================================================
    def subscribe(self, interface: mqtt):
        interface.subscribe(self.xGet, qos=1)
        interface.subscribe(self.xSet, qos=1)
        
    #=======================================================================
    # Hand the get and set messahes by updating the state
    #=======================================================================
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
        
    #===========================================================================
    # Send update message of state
    #===========================================================================
    def sendUpdate(self, interface: mqtt):
        res = {}
        res[twinProtocol.TWINSTATE] = self.xState.getState()
        s = json.dumps(res)
        interface.publish(self.xUpdate, s, retain=False, qos=1)
        
    #=======================================================================
    # Standard set filter is to allow all state fields to be updated
    #=======================================================================
    def setFilter(self, delta: dict):
        return delta
    
    #===========================================================================
    # Allow state to be deleted
    #===========================================================================
    def deleteAllowed(self, topic: str, payload: str):
        return True
    
    #===========================================================================
    # Attache an observer for the State Router
    #===========================================================================
    def attachObserver(self, obs: MQTTStateObserver):
        self.xObservers.append(obs)
        
    #===========================================================================
    # Detache an observer
    #===========================================================================
    def dettachObserver(self, obs: MQTTStateObserver):
        self.xObservers.remove(obs)    
        
    #===========================================================================
    # Notificaition of changes initiated by the router
    #===========================================================================
    def notifyObservers(self):
        for obs in self.xObservers:
            obs.stateNotify(self.xState)  
            
            
    #===========================================================================
    # Update state as a client request from a non MQTT request
    #===========================================================================
    def updateState(self, delta: dict, interface: mqtt = None):
        self.xState.updateState(delta)
        self.notifyObservers()
        if (interface):
            self.sendUpdate(interface)
        
    #===========================================================================
    # Return state as dictionary
    #===========================================================================
    def getState(self):
        return self.xState.getState()
    
    #===========================================================================
    # Handle a change notification on the state
    #===========================================================================
    def notify(self):
        self.sendUpdate(self.interface)
    