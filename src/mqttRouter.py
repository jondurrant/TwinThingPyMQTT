#===============================================================================
# mqttRouter - Suerclass to handle all routring of topic messages
# Jon Durrant
# 10-Jan-2022
#===============================================================================
import logging
import paho.mqtt.client as mqtt

class MQTTRouter:
    #===========================================================================
    # Constructor, requires the client id 
    #===========================================================================
    def __init__(self, client_id: str):
        self.xLogging = logging.getLogger(__name__)
        self.xClientId = client_id
        
    #=======================================================================
    # Called by the agent so that the router can setup the subscriptions it will listen too
    #=======================================================================
    def subscribe(self, interface: mqtt):
        self.xLogging.debug("Subscribe")
        
    #===========================================================================
    # Route a given message. If it is handle by the router return true else false
    #===========================================================================
    def route(self, topic: str, payload: str, interface: mqtt):
        self.xLogging.debug("Route")
        return False
        
    #===========================================================================
    # Get the client id
    #===========================================================================
    def getClientId(self):
        return self.xClientId