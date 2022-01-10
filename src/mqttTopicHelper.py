


MQTT_TOPIC_THING_HEADER="TNG"
MQTT_TOPIC_HEADER="TPC"
MQTT_TOPIC_LIFECYCLE="LC"
MQTT_TOPIC_GROUP_HEADER="GRP"
MQTT_TOPIC_LIFECYCLE_OFFLINE="OFF"
MQTT_TOPIC_LIFECYCLE_ONLINE="ON"
MQTT_TOPIC_LIFECYCLE_KEEP_ALIVE="KEEP"
MQTT_STATE_TOPIC="STATE"
MQTT_STATE_TOPIC_UPDATE="UPD"
MQTT_STATE_TOPIC_GET="GET"
MQTT_STATE_TOPIC_SET="SET"



#===============================================================================
# /***
#  * generate the lifecycle topic for thing
#  * @param id - id of the thing
#  * @param name  = name of the lifecycle topic (ON, OFF, KEEP)
#  */
#===============================================================================
def genLifeCycleTopic(id: str, name: str):
    return ("%s/%s/%s/%s"%(MQTT_TOPIC_THING_HEADER, id,
            MQTT_TOPIC_LIFECYCLE, name  ))


#===============================================================================
# /***
#  * Generate the thing topic full name
#  * @param id - string id of the thing
#  * @param name - string name of the topic
#  */
#===============================================================================
def genThingTopic(id: str, name: str):
    return ("%s/%s/%s/%s"%(MQTT_TOPIC_THING_HEADER, id,
            MQTT_TOPIC_HEADER, name))

#===============================================================================
# /***
#  * Generate the group topic full name
#  * @param grp - string of group anme
#  * @param name - string name of the topic
#  */
#===============================================================================
def genGroupTopic(grp: str, name: str):
    return ("%s/%s/%s/%s"%(
            MQTT_TOPIC_GROUP_HEADER,
            grp,
            MQTT_TOPIC_HEADER,
            name))

 #==============================================================================
 # * Generate update topic for thing
 # * @param id - Id of thing
 #==============================================================================
def getThingUpdate(id: str):
    return ("%s/%s/%s/%s"%(MQTT_TOPIC_THING_HEADER, id,
            MQTT_STATE_TOPIC, MQTT_STATE_TOPIC_UPDATE))


 #==============================================================================
 # * Generate get topic for thing
 # * @param id - Id of thing
 #==============================================================================
def getThingGet( id: str):
    return ("%s/%s/%s/%s"%(MQTT_TOPIC_THING_HEADER, id,
                 MQTT_STATE_TOPIC, MQTT_STATE_TOPIC_GET))


#===============================================================================
#  * Generate set topic for thing
#  * @param id - Id of thing
# 
#===============================================================================
def getThingSet(id: str):
    return ("%s/%s/%s/%s"%(MQTT_TOPIC_THING_HEADER, id,
                 MQTT_STATE_TOPIC, MQTT_STATE_TOPIC_SET))
    
    