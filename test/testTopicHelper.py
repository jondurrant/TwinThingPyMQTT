import unittest
import mqttTopicHelper as helper

id="TestId"


class TopicHelperTests(unittest.TestCase):
    
    
    def testLifecycle(self):
        topic = helper.genLifeCycleTopic(
            id,
            helper.MQTT_TOPIC_LIFECYCLE_ONLINE
            )
        self.assertEqual(topic, "TNG/"+id+"/LC/"+helper.MQTT_TOPIC_LIFECYCLE_ONLINE )
        topic = helper.genLifeCycleTopic(
            id,
            helper.MQTT_TOPIC_LIFECYCLE_OFFLINE
            )
        self.assertEqual(topic, "TNG/"+id+"/LC/"+helper.MQTT_TOPIC_LIFECYCLE_OFFLINE )
        
    def testThing(self):
        topic = helper.genThingTopic(id, "test");
        self.assertEqual(topic,
                         "TNG/"+id+"/TPC/test")
        topic = helper.getThingUpdate(id)
        self.assertEqual(topic, "TNG/"+id+"/STATE/UPD")
        topic = helper.getThingGet(id)
        self.assertEqual(topic, "TNG/"+id+"/STATE/GET")
        topic = helper.getThingSet(id)
        self.assertEqual(topic, "TNG/"+id+"/STATE/SET")
        
    def testGroup(self):
        topic = helper.genGroupTopic("ALL", "PING")
        self.assertEqual(topic, "GRP/ALL/TPC/PING")
        
if __name__ == '__main__':
    unittest.main()