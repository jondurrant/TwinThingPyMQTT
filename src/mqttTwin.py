#===============================================================================
# MQTTTwin - Derived version of a Twin Group that is used for the get function
# Allows full select capability on Twin
# Jon Durrant
# 12-Jan-2022
#===============================================================================
from mqttGroup import MQTTGroup

class MQTTTwin(MQTTGroup):
    def __init__(self, name: str):
        self.name = name
        
    def getGroupTwinIds(self, session):
        return [self.name]