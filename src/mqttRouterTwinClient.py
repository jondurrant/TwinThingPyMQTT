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
import threading


class MQTTRouterTwinClient(MQTTRouter):
    
    
    def __init__(self, client_id: str, group: str, interface: mqtt, options:dict={}):
        super().__init__(client_id)
        threading.Thread.__init__(self)
        self.xLock = threading.Lock()
       
        self.xLogging = logging.getLogger(__name__)
        
        self.xSet = topicHelper.getTwinGroupSet(group)
        self.xGet = topicHelper.getTwinGroupGet(group)
        self.xRes = topicHelper.getTwinGroupResult(group)
        self.xQueryCount = 0
        self.xInterface = interface
        self.xResults={}
        #All in Milliseconds
        self.xOptions = {
            "cacheTime": options.get("cacheTime", 5000),
            "queryTimout": options.get("queryTimout", 5000),
            "queryCheck": options.get("queryCheck", 100)
            }
        
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
            self.resultCacheHousekeeping()
            
            j = json.loads(payload)
            if ('query' in j):
                query = j['query']
                self.resultCacheAdd(query, j)
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
        res = self.resultCacheGetRm(query)
        while (res == None):
            time.sleep(self.xOptions["queryCheck"]/1000)
            i=i+ self.xOptions["queryCheck"]
            if (i > self.xOptions["queryTimout"]):
                return {"error": True}
            res = self.resultCacheGetRm(query)
        return res
     
    def update(self, delta: dict = {}, target=[]):   
         
        j = {
            'delta': delta,
            'from': target
            }
        
        p = json.dumps(j)
        self.xLogging.debug("Publishing: %s - %s"%(self.xSet,p))
        self.xInterface.publish(self.xSet, p, retain=False, qos=1)
        
        
    def resultCacheAdd(self, key: str, d: dict):
        d["touch"]=self.timestampMs()
        with self.xLock:  
            self.xResults[key]=d
            
    def resultCacheGetRm(self, key: str):
        with self.xLock:  
            if key in self.xResults:
                res = self.xResults[key]
                del self.xResults[key]
                return res
        return None
    
    def resultCacheHousekeeping(self):
        t = self.timestampMs()
        self.xLogging.debug("Cache Size %d"%len(self.xResults))
        
        with self.xLock:
            rmList = []
            for key in self.xResults:
                rec = self.xResults[key]
                if "touch" in rec:
                    if (t > (rec["touch"]+self.xOptions["cacheTime"])):
                        rmList.append(key)
                else:
                    #No touch data so delete always
                    rmList.append(key)
                    
            for key in rmList:
                self.xLogging.debug("Housekeeping removed %s"%key)
                del self.xResults[key]   
                
             
    
             
    def timestampMs(self):
        return time.time_ns()/1000