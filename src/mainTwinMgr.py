from mqttAgent import  MQTTAgent
import logging
from mqttObserver import MQTTObserver
from mqttRouterPing import MQTTRouterPing
from mqttRouterState import MQTTRouterState
from mqttRouterTwin import MQTTRouterTwin

from twinState import TwinState

logging.basicConfig(level="DEBUG")

mqttUser="twinmgt"
mqttPwd="test"
mqttTarget= "nas3"
mqttPort=1883

dbUser = "oracrad"
dbPwd ="Hm4CeqH7hkUf"
dbHost = "nas3"
dbPort = 3307
dbSchema = "OracRad"


state = TwinState()
state.setState({
    'trn': 1,
    'things': 0,
    'cache': 0
    })


mqttObs = MQTTObserver()
pingRouter = MQTTRouterPing(mqttUser)
stateRouter = MQTTRouterState(mqttUser, state)
twinRouter = MQTTRouterTwin(mqttUser, dbHost, dbPort, dbSchema, dbUser, dbPwd )


mqttAgent = MQTTAgent(mqttUser)
mqttAgent.credentials(mqttUser, mqttPwd)
mqttAgent.mqttHub(mqttTarget, mqttPort, True)
mqttAgent.addObserver(mqttObs)
mqttAgent.addRouter(pingRouter)
mqttAgent.addRouter(stateRouter)
mqttAgent.addRouter(twinRouter)

mqttAgent.start()