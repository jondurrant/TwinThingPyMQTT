from mqttAgent import  MQTTAgent
import logging
from mqttObserver import MQTTObserver
from mqttRouterPing import MQTTRouterPing
from twinMgrStateRouter import TwinMgrStateRouter
from mqttRouterTwin import MQTTRouterTwin

from twinState import TwinState
import threading

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

mqttAgent = MQTTAgent(mqttUser)
mqttAgent.credentials(mqttUser, mqttPwd)
mqttAgent.mqttHub(mqttTarget, mqttPort, True)

mqttObs = MQTTObserver()
pingRouter = MQTTRouterPing(mqttUser)
stateRouter = TwinMgrStateRouter(mqttUser, state, mqttAgent)
twinRouter = MQTTRouterTwin(state, mqttUser, dbHost, dbPort, dbSchema, dbUser, dbPwd )



mqttAgent.addObserver(mqttObs)
mqttAgent.addRouter(pingRouter)
mqttAgent.addRouter(stateRouter)
mqttAgent.addRouter(twinRouter)

xTimer = None
def housekeeping():
    print("Housekeeping")
    twinRouter.cacheHousekeeping(60.0*15)
    xTimer = threading.Timer(60.0*60.0, housekeeping)
    xTimer.start()

xTimer = threading.Timer(60.0*15, housekeeping)
xTimer.start()


mqttAgent.start()