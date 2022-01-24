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
    
    #===========================================================================
    # query all thing twin records in the group.
    # select: list of column names to bring back. top level is {clientId, reported,
    #   desired, rejected}. Can also pull back json objects inside using dot notation.
    #   for example "reported.clock"
    # asColumn: list of string names of names to rename columns too. Recomended to use
    # where: dictuary of where clause. Basic clause is of form {'column': "reported.temp", 'op': ">", 'value': 10}
    #   may also include nested queries in logic {'and': [where, where]} or {'or': [where, where]}
    # orient: format of responce (pandas format): "split", "records", "index", "values", "table", "columns"
    #===========================================================================
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
     
    #===========================================================================
    # update all things in the group to have the delta
    # delta: dictionary of kust of state variables to change e.g.{'on': True}
    # target: list of things to target by clientId. empty list means all of group
    #===========================================================================
    def update(self, delta: dict = {}, target=[]):   
         
        j = {
            'delta': delta,
            'from': target
            }
        
        p = json.dumps(j)
        self.xLogging.debug("Publishing: %s - %s"%(self.xSet,p))
        self.xInterface.publish(self.xSet, p, retain=False, qos=1)
        
        
    #===========================================================================
    # Result cache handling to covert async call to sync request
    # Store dictionary under key
    #===========================================================================
    def resultCacheAdd(self, key: str, d: dict):
        d["touch"]=self.timestampMs()
        with self.xLock:  
            self.xResults[key]=d
            
    #===========================================================================
    # Check if result is in cache. If it is return it and drop from the cache
    # if it isn't in the cache return None
    #===========================================================================
    def resultCacheGetRm(self, key: str):
        with self.xLock:  
            if key in self.xResults:
                res = self.xResults[key]
                del self.xResults[key]
                return res
        return None
    
    #===========================================================================
    # Housekeep the cache by removing any older cached queries that where not removed
    # We may not be the only people asking queries of the thing
    #===========================================================================
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
                
             
    
    #==================================================================
    # Return a timestamp in ms
    #==================================================================
    def timestampMs(self):
        return time.time_ns()/1000