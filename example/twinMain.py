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

mqttUser="nob"
mqttPwd="nob"
mqttTarget="nas3"
mqttPort=1883


state = TwinState()
state.setState({
    'trn': 0,
    'ok': True,
    'count': 0,
    'on': False
    })

mqttAgent = MQTTAgent(mqttUser)
mqttAgent.credentials(mqttUser, mqttPwd)
mqttAgent.mqttHub(mqttTarget, mqttPort, True)


mqttObs = MQTTObserver()
stateObs = ExampleStateObserver()
pingRouter = MQTTRouterPing(mqttUser)
stateRouter = ExampleStateRouter(mqttUser, state, mqttAgent) #MQTTRouterState(mqttUser, state)
stateRouter.attachObserver(stateObs)


mqttAgent.addObserver(mqttObs)
mqttAgent.addRouter(pingRouter)
mqttAgent.addRouter(stateRouter)


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

mqttAgent.start()


'''
//Set up the credentials so we have an ID for our thing
mqttAgent.credentials(pMqttUser, mqttPwd);
mqttRouter.init(mqttAgent.getId(), &mqttAgent);

//Twin agent to manage the state
xTwin.setStateObject(&state);
xTwin.setMQTTInterface(&mqttAgent);
xTwin.start(tskIDLE_PRIORITY+1);
xTwin.setTopics(mqttRouter.getGroupTopicOn(), mqttRouter.getGroupTopicOff());

//Start up a Ping agent to mange ping requests
xPing.setInterface(&mqttAgent);
xPing.start(tskIDLE_PRIORITY+1);

//Give the router the twin and ping agents
mqttRouter.setTwin(&xTwin);
mqttRouter.setPingTask(&xPing);

//Setup and start the mqttAgent
//mqttAgent.setObserver(&agentObs);
mqttAgent.setObserver(&xLedMgr);
mqttAgent.setRouter(&mqttRouter);
mqttAgent.connect(mqttTarget, mqttPort, true);
mqttAgent.start(tskIDLE_PRIORITY+1);
'''



