from mqttRouterState import MQTTRouterState


class TwinMgrStateRouter(MQTTRouterState):
        
    
    def setFilter(self, delta: dict):
        res = {'trn': delta.get('trn', 0)}

        return res
    
    def deleteAllowed(self, topic: str, payload: str):
        return False
    