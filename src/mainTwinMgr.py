from mqttAgent import  MQTTAgent
import logging
from mqttObserver import MQTTObserver
from mqttRouterPing import MQTTRouterPing
from mqttRouterState import MQTTRouterState
from mqttRouterTwin import MQTTRouterTwin

from twinState import TwinState

logging.basicConfig(level="DEBUG")

mqttUser="super"
mqttPwd="test"
mqttTarget="nas3"
mqttPort=1883


state = TwinState()
state.setState({
    'trn': 1,
    'things': 0,
    'cache': 0
    })


mqttObs = MQTTObserver()
pingRouter = MQTTRouterPing(mqttUser)
stateRouter = MQTTRouterState(mqttUser, state)
twinRouter = MQTTRouterTwin(mqttUser)


mqttAgent = MQTTAgent(mqttUser)
mqttAgent.credentials(mqttUser, mqttPwd)
mqttAgent.mqttHub(mqttTarget, mqttPort, True)
mqttAgent.addObserver(mqttObs)
mqttAgent.addRouter(pingRouter)
mqttAgent.addRouter(stateRouter)
mqttAgent.addRouter(twinRouter)

mqttAgent.start()