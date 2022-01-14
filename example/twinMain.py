#===============================================================================
# Example Thing
#===============================================================================

from mqttAgent import  MQTTAgent
import logging
from mqttObserver import MQTTObserver
from mqttRouterPing import MQTTRouterPing
from mqttRouterState import MQTTRouterState
from exampleStateRouter import ExampleStateRouter
from exampleStateObserver import ExampleStateObserver
import threading

from twinState import TwinState

logging.basicConfig(level="DEBUG")


#MQTT Credentials and targets
mqttUser="nob"
mqttPwd="nob"
mqttTarget="nas3"
mqttPort=1883

#Setup the twin state
state = TwinState()
state.setState({
    'trn': 0,
    'ok': True,
    'count': 0,
    'on': False
    })

#The MQTT Client Agent
mqttAgent = MQTTAgent(mqttUser)
mqttAgent.credentials(mqttUser, mqttPwd)
mqttAgent.mqttHub(mqttTarget, mqttPort, True)

#Consigure the observers and routers
mqttObs = MQTTObserver()
stateObs = ExampleStateObserver()
pingRouter = MQTTRouterPing(mqttUser)
stateRouter = ExampleStateRouter(mqttUser, state, mqttAgent) #MQTTRouterState(mqttUser, state)
stateRouter.attachObserver(stateObs)

#Add observers and reouter to client agent
mqttAgent.addObserver(mqttObs)
mqttAgent.addRouter(pingRouter)
mqttAgent.addRouter(stateRouter)

#Set up a time to update the state locally
xTimer = None
def tick():
    delta = {
        'count': stateRouter.getState()['count'] +1
    }
    stateRouter.updateState(delta, mqttAgent)
    xTimer = threading.Timer(5.0, tick)
    xTimer.start()


xTimer = threading.Timer(5.0, tick)
xTimer.start()


#Start the client agent
mqttAgent.start()




