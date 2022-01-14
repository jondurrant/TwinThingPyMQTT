#===============================================================================
# ExampleStateObserver - Example state observer will just print state on change
# Jon Durrant
# 14-Jan-2022
#===============================================================================
from mqttStateObserver import MQTTStateObserver
from twinState import TwinState
import json



class ExampleStateObserver(MQTTStateObserver):
    
    def stateNotify(self, state: TwinState):
        j = state.getState()
        print("State changed to: %s\n"%json.dumps(j,  sort_keys=True))