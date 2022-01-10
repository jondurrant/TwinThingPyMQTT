#===============================================================================
# mqttRouter - Suerclass to handle all routring of topic messages
# Jon Durrant
# 10-Jan-2022
#===============================================================================
import logging
import paho.mqtt.client as mqtt

class MQTTRouter:
    def __init__(self, client_id: str):
        self.xLogging = logging.getLogger(__name__)
        self.xClientId = client_id
        
    def subscribe(self, interface: mqtt):
        self.xLogging.debug("Subscribe")
        
    def route(self, topic: str, payload: str, interface: mqtt):
        self.xLogging.debug("Route")
        return False
        
    
    def getClientId(self):
        return self.xClientId