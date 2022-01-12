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
from twinDb import TwinDb
from mqttGroup import MQTTGroup
from mqttTwin import MQTTTwin
import twinProtocol
import json
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class MQTTRouterTwin(MQTTRouter):
    
    
    def __init__(self, client_id: str, dbHost: str, dbPort: int, dbSchema: str,
                 dbUser: str, dbPwd: str):
        super().__init__(client_id)
        self.xLogging = logging.getLogger(__name__)
        
        self.xSet = topicHelper.getTwinSet("+")
        self.xGet = topicHelper.getTwinGet("+")
        
        self.xLC = topicHelper.genLifeCycleTopic("+", topicHelper.MQTT_TOPIC_LIFECYCLE_ONLINE)
        self.xUpdate = topicHelper.getThingUpdate("+")
        
        self.xGrpSet = topicHelper.getTwinGroupSet("+")
        self.xGrpGet = topicHelper.getTwinGroupGet("+")
        
        self.xCache = {}
        
        self.connectStr='mysql+pymysql://%s:%s@%s:%d/%s'%(
            dbUser,
            dbPwd,
            dbHost,
            dbPort,
            dbSchema
            )
        self.session=None
        self.openDb()
        
    def openDb(self):
        try:
            engine = create_engine(self.connectStr)
            session = sessionmaker()
            session.configure(bind=engine)
            self.session=session()
        except exc.SQLAlchemyError:
            self.xLogging.debug("Failed to open DB")
            self.session = None
        
       
    def subscribe(self, interface: mqtt):
        interface.subscribe(self.xGet, qos=1)
        interface.subscribe(self.xSet, qos=1)
        interface.subscribe(self.xLC, qos=1)
        interface.subscribe(self.xUpdate, qos=1)
        interface.subscribe(self.xGrpGet, qos=1)
        interface.subscribe(self.xGrpSet, qos=1)
        
        
    def route(self, topic: str, payload: str, interface: mqtt):
        #Twin  Get
        if ( topicHelper.topicEquals(self.xGet, topic)):
            target = self.tngTarget(topic)
            j = json.loads(payload)
            if ("select" in j):
                target = self.tngTarget(topic)
                j = json.loads(payload)
                self.twinGet(target, j, interface)
            else:
                twin = self.getTwin(target)
                self.pubUpdated(target, twin, interface)
                
            return True
        
        #Twin Set
        if ( topicHelper.topicEquals(self.xSet, topic)):
            target = self.tngTarget(topic)
            j = json.loads(payload)
            self.twinSet(target, j, interface)
            return True
        
        #THing Online Sequence
        if ( topicHelper.topicEquals(self.xLC, topic)):
            target = self.tngTarget(topic)
            if (not self.isNewTwin(target)):
                
                twin = self.getTwin(target)
                setTopic = topicHelper.getThingSet(target)
                setState = {'state': twin.getReportedState()}
                #setState = {'delta': twin.getReportedState()}
                self.xLogging.debug("Set state on returning thing %s state %s"%(target, json.dumps(setState,sort_keys=True) ))
                interface.publish(setTopic, json.dumps(setState), retain=False, qos=1)
                
                if (not twin.isUptoDate()):
                    deltaState = {'delta': twin.getDelta()}
                    self.xLogging.debug("Set delta for returning thing %s delta %s"%(target, json.dumps(deltaState,sort_keys=True)))
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
            
            self.xLogging.debug("Twin %s Reported %s"%(target, json.dumps(twin.getReportedState(), sort_keys=True)))
            self.pubUpdated(target, twin, interface)
            self.storeTwin(twin)
            return True
        
        #Group Set
        if (topicHelper.topicEquals(self.xGrpSet, topic)):
            grp = self.tngTarget(topic)
            j = json.loads(payload)
            self.groupSet(grp, j, interface)
            
        #Group Get
        if (topicHelper.topicEquals(self.xGrpGet, topic)):
            grp = self.tngTarget(topic)
            j = json.loads(payload)
            self.groupGet(grp, j, interface)
        
        return False
        

    def tngTarget(self, topic: str):
        target = topic.split("/")[1]
        
        return target
    
    def getTwin(self, target: str):
        if (not target in self.xCache):
            self.xCache[target] = TwinDb(target)
            try:
                self.xCache[target].loadFromDb(self.session)
            except exc.SQLAlchemyError:
                self.xLogging.error("Failed to read from DB, reopen")
                self.openDb()
                
            self.xLogging.debug("Added to Cache %s"%target)
        return self.xCache[target]
      
    def isNewTwin(self, target: str):
        if (not target in self.xCache):
            twin = TwinDb(target)
            self.xCache[target] = twin
            try:
                if (twin.loadFromDb(self.session)):
                    return False
                else:
                    return True
            except exc.SQLAlchemyError:
                self.xLogging.error("Failed to read from DB, reopen")
                self.openDb()
                
            return True
        else:       
            return False
    
    def pubUpdated(self, target: str, twin: TwinDb, interface: mqtt):
        upd = { "desired": twin.getDesiredState(),
               "desiredMeta": twin.getDesiredMeta(),
               "reported": twin.getReportedState(),
               "reportedMeta": twin.getReportedMeta(),
               "declined": twin.getDeclinedState(),
               "declinedMeta": twin.getDeclinedMeta()
        }
        updTopic = topicHelper.getTwinUpdate(target)
        interface.publish(updTopic, json.dumps(upd), retain=False, qos=1)
            
    def storeTwin(self, twin: TwinDb):  
        try:
            twin.updateDb(self.session)
        except exc.SQLAlchemyError:
            self.xLogging.error("Failed to write to DB, reopen")
            self.openDb()
       
       
    def twinSet(self, target: str, j: dict, interface: mqtt):
        twin = self.getTwin(target)
        newStates = {}
        if ("set" in j):
            newStates = j["set"]
        elif ("delta" in j):
            newStates = j["delta"]
        elif ("state" in j):
            newStates = j["state"]
        else:
            self.xLogging.error("Unknown format for set  %s"%json.dumps(j))
            return 
        
        #Update twin
        self.xLogging.debug("Updating with %s"%json.dumps(newStates, sort_keys=True))
        twin.updateDesiredState(newStates)
        self.storeTwin(twin)
        self.pubUpdated(target, twin, interface)
        
        #Update thing
        setTopic = topicHelper.getThingSet(target)
        delta = json.dumps({"delta": twin.getDelta()})
        self.xLogging.debug("Sending Thing delta->  %s"%delta)
        interface.publish(setTopic, delta, retain=False, qos=1)
                
    
    def groupSet(self, grp: str, d: dict, interface: mqtt):
        mGroup = MQTTGroup(grp)
        targets = mGroup.getGroupTwinIds(self.session)
        
        for target in targets:
            self.setTwin(target, d, interface)
            
    def groupGet(self, grp: str, d: dict, interface: mqtt):
        mGroup = MQTTGroup(grp)
        select = d.get("select", ["*"])
        columnAs = d.get("as",  [])           
        where = d.get("where", {})
        orient = d.get("orient", "records")
        query = d.get("query", 0)                 

        s = mGroup.selectTwinFrame(self.session, select, columnAs, where, orient)
        j = {
                "query": query,
                "res": json.loads(s)
            }
        topic = topicHelper.getTwinGroupResult(grp)
        interface.publish(topic, json.dumps(j), retain=False, qos=1)
        
        
    def twinGet(self, target: str, d: dict, interface: mqtt):
        mTwin = MQTTTwin(target)
        select = d.get("select", ["*"])
        columnAs = d.get("as",  [])           
        where = d.get("where", {})
        orient = d.get("orient", "records")
        query = d.get("query", 0)                 

        s = mTwin.selectTwinFrame(self.session, select, columnAs, where, orient)
        j = {
                "query": query,
                "res": json.loads(s)
            }
        topic = topicHelper.getTwinResult(target)
        interface.publish(topic, json.dumps(j), retain=False, qos=1)
            