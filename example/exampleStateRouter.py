from mqttRouterState import MQTTRouterState


class ExampleStateRouter(MQTTRouterState):
        
    
    def setFilter(self, delta: dict):
        res = {'trn': delta.get('trn', 0)}
        if ('on' in delta):
            res['on'] = delta['on']
        return res
    
    def deleteAllowed(self, topic: str, payload: str):
        return False
    