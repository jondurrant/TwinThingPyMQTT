from mqttAgent import  MQTTAgent
import logging

logging.basicConfig(level="DEBUG")

mqttUser="nob"
mqttPwd="nob"
mqttTarget="nas3"
mqttPort=1883



mqttAgent = MQTTAgent(mqttUser)
mqttAgent.credentials(mqttUser, mqttPwd)
mqttAgent.mqttHub(mqttTarget, mqttPort, True)


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