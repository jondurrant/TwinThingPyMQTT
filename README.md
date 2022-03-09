# TwinThingPyMQTT
Twin Thing Python framework against MQTT. Plus TwinMgr to manage a central
digital twin.

## Framework

MQTT Framework in Python to produce IoT MQTT clients to the same spec as my C++ library for Raspberry Pi PICO [TwinThingsPicoESP](https://github.com/jondurrant/twinThingPicoESP).

Clients operate as IoT clients with state and operate on a standard set of topics to report, request and set state.

## TwinMgr
TwinMgr uses the Framework to provide a local digital twin of a device. Clients can then operate through the digital twin rather than direct to client. This has the advantage that the twin will hold state until the device becomes available and then update the device.

The TwinMgt can also operate on devices in a group. Including pull back all states for the group or seting particular attributes on all devices within the group.

# Dependencies - Python
+ Python3
+ dotmap
+ numpy
+ paho-mqtt
+ pandas
+ PyMySQL
+ pyOpenSSL
+ SQLAlchemy
+ [twinThing](https://github.com/jondurrant/twinThing) 
+ mysql Db
+ [emqx](https://www.emqx.io/) using Mysql authentication 

# File Structure
+ src/ - library files
+ src/mainTwinMgr.py - main program for the Twin Manager
+ example/ - Simple example of a stateful IoT client
+ exp/ - Experimental code
+ lib/ - non pip packages used by the code. My twinThing library
+ test/ - some test python scripts to interact with the TwinMgt
+ ddl/ - mysql table structure.


# Deployment - TwinMgr
Dockerfile to build the TwinMgr as a docker image is included.

TwinMgt expects some environment variables to be setup. These are:
+ MQTT_USER - Username and Client Id to connect to MQTT
+ MQTT_PASSWD - Password to authenticate against MQTT
+ MQTT_HOST - Hostname of MQTT server
+ MQTT_PORT - Port that MQTT is listen on, normally 1883
+ MQTT_CERT - If using SSL, then the SSL chain certificate to validate against
+ TWIN_DB_USER - Username for database containing the Twin table and the EMQX ACL
+ TWIN_DB_PASSWD - Password to authenticate against database
+ TWIN_DB_HOST - Database host name
+ TWIN_DB_PORT - Database port
+ TWIN_DB_SCHEMA - Schema used for the Twin table and the EMQX tables


# MQTT Server
Though the framework will work with any MQTT the TwinMgr is specific to EMQX running with MySQl authentication. This is because it uses the group topic ACL to identify which devices are in which group.

## Topic Structure
I've tried to condence literals a bit. 

TNG/<ID>/ - THING / ID, same as user name in my example
TNG/<ID>/LC - LC is lifecycle and annouces connection and disconnection
TNG/<ID>/TPC - TOPIC, for messaging to a specific thing

Example assuming you name the pico as "pico"
+ TNG/pico/TPC/PING - ping re	quest sent to pico
+ TNG/pico/TPC/PONG - pong as response to the ping

Group topics also exist in the structure under.

GRP/<Group>/TPC/ - Topics to talk to group of devices

Examle:
GRP/ALL/TPC/PING - ping topic that all IoT devices listen for.

The TwinMgr add topics to a thing of:
TNG/<ID>/TWIN/GET - Get twin state
TNG/<ID>/TWIN/SET - Set twin state
TNG/<ID>/TWIN/UPD - Reports result of get (provides desired, reported and declined versions of state plus metadata)
TNG/<ID>/TWIN/RES - If query language is used for GET then response sent to RES rather than update

Add group topics of:
GRP/<GRP>/TWIN/GET - using group query language
GRP/<GRP>/TWIN/SET - using group query language
GRP/<GRP>/TWIN/RES - result of get

See test/things as examples of test code which execute these topic APIs.

## Clients
You will need to setup users and permissions for your clients.

I run the default rule to deny everything unless otherwise granted:
Default rule: {
	  "topic": "#",
	  "action": "pubsub",
	  "access": "deny"
	}

A device requires the following permissions to be able to operate:
[
	{
	  "topic": "GRP/ALL/TPC/#",
	  "action": "sub",
	  "access": "allow"
	},
	{
	  "topic": "TNG/$CLIENTID/#",
	  "action": "pubsub",
	  "access": "allow"
	}
]

To give a device access to a group called "saber" the following permissions are required:
[
	{
	  "topic": "GRP/saber/TPC/#",
	  "action": "pubsub",
	  "access": "allow"
	}
]

The TwinMgr requires the following permissions to pubsub to every device and to be able operate the TWIN topic channels both under a device and under group heirachy.
[
	{
	  "topic": "GRP/+/TWIN/#",
	  "action": "pubsub",
	  "access": "allow"
	},
	{
	  "topic": "TNG/+/STATE/UPD",
	  "action": "sub",
	  "access": "allow"
	},
	{
	  "topic": "TNG/+/TWIN/#",
	  "action": "pubsub",
	  "access": "allow"
	}
]




