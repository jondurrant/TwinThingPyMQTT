#===============================================================================
# MQTTStateObserver - Supertype and API for state notifications
# Jon Durrant
# 14-Jan-2021
#===============================================================================
from twinState import TwinState

class MQTTStateObserver:
    
    def stateNotify(self, state: TwinState):
        return