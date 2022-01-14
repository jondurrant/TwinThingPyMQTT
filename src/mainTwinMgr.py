#===============================================================================
# Client for a Twin Mgr to cache state of things and provide query capability
# Jon Durrant
# 14-Jan-2022
#===============================================================================
from mqttAgent import  MQTTAgent
import logging
from mqttObserver import MQTTObserver
from mqttRouterPing import MQTTRouterPing
from twinMgrStateRouter import TwinMgrStateRouter
from mqttRouterTwin import MQTTRouterTwin

from twinState import TwinState
import threading

#Debug level
logging.basicConfig(level="DEBUG")


#Credentials = needs to look at picking up from network
mqttUser="twinmgt"
mqttPwd="test"
mqttTarget= "nas3"
mqttPort=1883

dbUser = "oracrad"
dbPwd ="Hm4CeqH7hkUf"
dbHost = "nas3"
dbPort = 3307
dbSchema = "OracRad"


#Setup the state. Have some stats on behaviour
state = TwinState()
state.setState({
    'trn': 1,
    'things': 0,
    'cache': 0
    })

#Setup the Client Agent
mqttAgent = MQTTAgent(mqttUser)
mqttAgent.credentials(mqttUser, mqttPwd)
mqttAgent.mqttHub(mqttTarget, mqttPort, True)

#Set up the observers and routers
mqttObs = MQTTObserver()
pingRouter = MQTTRouterPing(mqttUser)
stateRouter = TwinMgrStateRouter(mqttUser, state, mqttAgent)
twinRouter = MQTTRouterTwin(state, mqttUser, dbHost, dbPort, dbSchema, dbUser, dbPwd )

#Add observers and reotuers to the agent
mqttAgent.addObserver(mqttObs)
mqttAgent.addRouter(pingRouter)
mqttAgent.addRouter(stateRouter)
mqttAgent.addRouter(twinRouter)

#Timer for housekeeping
xTimer = None
def housekeeping():
    print("Housekeeping")
    twinRouter.cacheHousekeeping(60.0*15)
    xTimer = threading.Timer(60.0*60.0, housekeeping)
    xTimer.start()

xTimer = threading.Timer(60.0*15, housekeeping)
xTimer.start()

#Start the agent
mqttAgent.start()