
from mqttStateObserver import MQTTStateObserver
from twinState import TwinState
import json



class ExampleStateObserver(MQTTStateObserver):
    
    def stateNotify(self, state: TwinState):
        j = state.getState()
        print("State changed to: %s\n"%json.dumps(j,  sort_keys=True))