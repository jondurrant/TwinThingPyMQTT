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
import os

from twinState import TwinState

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL, 
                    format= '[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s')


#MQTT Credentials and targets
#Credentials = needs to look at picking up from network
mqttUser=os.environ.get("MQTT_USER")
mqttPwd=os.environ.get("MQTT_PASSWD")
mqttTarget= os.environ.get("MQTT_HOST")
mqttPort=int(os.environ.get("MQTT_PORT"))
mqttCert=os.environ.get("MQTT_CERT", None)
tls=""
if (mqttCert != None):
    tls="TLS"
print("MQTT %s:%d %s - %s\n"%(mqttTarget,mqttPort,tls,mqttUser))

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
mqttAgent.mqttHub(mqttTarget, mqttPort, True, mqttCert)

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




