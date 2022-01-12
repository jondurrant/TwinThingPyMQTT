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
        
        
    def testTwin(self):
        topic = helper.getTwinGet(id)
        self.assertEqual(topic, "TNG/"+id+"/TWIN/GET")
        topic = helper.getTwinSet(id)
        self.assertEqual(topic, "TNG/"+id+"/TWIN/SET")
        topic = helper.getTwinUpdate(id)
        self.assertEqual(topic, "TNG/"+id+"/TWIN/UPD")
        topic = helper.getTwinResult(id)
        self.assertEqual(topic, "TNG/"+id+"/TWIN/RES")
        
    def testTopicEquals(self):
        self.assertEqual(helper.topicEquals("TNG/foo/STATE/GET", "TNG/foo/STATE/GET"), True)
        self.assertEqual(helper.topicEquals("TNG/foo/STATE/GET", "TNG/foo/STATE/SET"), False)
        
        self.assertEqual(helper.topicEquals("TNG/foo/STATE/#", "TNG/foo/STATE/GET"), True)
        self.assertEqual(helper.topicEquals("TNG/foo/STATE/#", "TNG/Jim/STATE/SET"), False)
        
        self.assertEqual(helper.topicEquals("TNG/foo/#", "TNG/foo/STATE/GET"), True)
        self.assertEqual(helper.topicEquals("TNG/foo/#", "TNG/Jim/STATE/SET"), False)
        
        self.assertEqual(helper.topicEquals("TNG/+/STATE/GET", "TNG/foo/STATE/GET"), True)
        self.assertEqual(helper.topicEquals("TNG/foo/+/GET", "TNG/foo/STATE/GET"), True)
        self.assertEqual(helper.topicEquals("TNG/foo/+/GET", "TNG/foo/STATE/SET"), False)
        self.assertEqual(helper.topicEquals("TNG/foo/STATE/+", "TNG/foo/STATE/SET"), True)
        self.assertEqual(helper.topicEquals("TNG/foo/STATE/+", "TNG/jim/STATE/SET"), False)
        
    def testTwinGroup(self):    
        grp="ALL"
        topic = helper.getTwinGroupGet(grp)
        self.assertEqual(topic, "GRP/"+grp+"/TWIN/GET")
        topic = helper.getTwinGroupSet(grp)
        self.assertEqual(topic, "GRP/"+grp+"/TWIN/SET")
        topic = helper.getTwinGroupResult(grp)
        self.assertEqual(topic, "GRP/"+grp+"/TWIN/RES")
    
if __name__ == '__main__':
    unittest.main()