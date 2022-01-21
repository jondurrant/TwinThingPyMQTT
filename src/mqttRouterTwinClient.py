#===============================================================================
# mqttRouterTwinClient - Router for client  Twin State Cache Management
# Jon Durrant
# 20-Jan-2022
#===============================================================================
import logging
import paho.mqtt.client as mqtt
from mqttRouter import MQTTRouter 
import mqttTopicHelper as topicHelper
import json
import time


class MQTTRouterTwinClient(MQTTRouter):
    
    
    def __init__(self, client_id: str, group: str, interface: mqtt):
        super().__init__(client_id)
       
        self.xLogging = logging.getLogger(__name__)
        
        self.xSet = topicHelper.getTwinGroupSet(group)
        self.xGet = topicHelper.getTwinGroupGet(group)
        self.xRes = topicHelper.getTwinGroupResult(group)
        self.xQueryCount = 0
        self.xInterface = interface
        self.xResults={}
        
    #===========================================================================
    # Suscribe to the Get and Set topics for the thing
    #===========================================================================
    def subscribe(self, interface: mqtt):
        interface.subscribe(self.xRes, qos=1)


    #=======================================================================
    # Hand the res message
    #=======================================================================
    def route(self, topic: str, payload: str, interface: mqtt):
        if (topic == self.xRes):
            self.xLogging.debug("Payload: %s"%payload)
            j = json.loads(payload)
            if ('query' in j):
                query = j['query']
                self.xResults[query]=j
            return True
        
        return False
    
    def query(self, select: list=["clientId"], asColumns: list=[], where: dict={}, orient: str="split" ):
        query = "%s:%d"%(self.getClientId(), self.xQueryCount)
        self.xQueryCount = self.xQueryCount + 1
        j = {
            'select': select, 
            'as': asColumns,
            'where': where,
            'orient': orient,
            'query': query
            }
        
        p = json.dumps(j)
        self.xLogging.debug("Publishing: %s"%p)
        self.xInterface.publish(self.xGet, p, retain=False, qos=1)
        
        i=0
        while (not query in self.xResults):
            time.sleep(0.1)
            i=i+1
            if (i > 10):
                return {"error": True}
        
        res = self.xResults[query]
        del self.xResults[query]
        return res
     
    def update(self, delta: dict = {}, target=[]):   
         
        j = {
            'delta': delta,
            'from': target
            }
        
        p = json.dumps(j)
        self.xLogging.debug("Publishing: %s"%p)
        self.xInterface.publish(self.xSet, p, retain=False, qos=1)