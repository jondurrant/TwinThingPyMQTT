#===============================================================================
# ExampleStateRouter - Example State Router,
# Needed so we can restrict which states can be updated. Only "On" state and
# trn are allowed.
# Jon Durrant
# 14-Jan-2022
#===============================================================================
from mqttRouterState import MQTTRouterState


class ExampleStateRouter(MQTTRouterState):
        
    #===========================================================================
    # setFilter - Filter a set request
    # Delta = dictionary of the update
    # returns = new dictionary with only valid update fields included
    #===========================================================================
    def setFilter(self, delta: dict):
        res = {'trn': delta.get('trn', 0)}
        if ('on' in delta):
            res['on'] = delta['on']
        return res
    
    #===========================================================================
    # Can a remote request allow the full state to be deleted (this is done in a set
    #===========================================================================
    def deleteAllowed(self, topic: str, payload: str):
        return False
    