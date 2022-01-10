#===============================================================================
# mqttObserver - Observe state of the MQTT COnnection
# Jon Durrant
# 10-Jan-2022
#===============================================================================
import logging

class MQTTObserver:
    def __init__(self):
        self.xLogging = logging.getLogger(__name__)
        
    def online(self):
        self.xLogging.debug("Online")
        
    def offline(self):
        self.xLogging.debug("Offline")
        
    def received(self):
        self.xLogging.debug("Received Message")
      
    def sent(self):
        self.xLogging.debug("Sent Message")  