#===============================================================================
# TwinMgrStateRouter - State Router for Twin management, preventing Sets
# Jon Durrant
# 14-Jan-2022
#===============================================================================
from mqttRouterState import MQTTRouterState


class TwinMgrStateRouter(MQTTRouterState):
        
    
    #===========================================================================
    # Filter any sets apart from the trn id.
    #===========================================================================
    def setFilter(self, delta: dict):
        res = {'trn': delta.get('trn', 0)}

        return res
    
    #===========================================================================
    # PRevent del of the state
    #===========================================================================
    def deleteAllowed(self, topic: str, payload: str):
        return False
    