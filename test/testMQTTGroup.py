import unittest
from mqttGroup import MQTTGroup
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


connectStr='mysql+pymysql://%s:%s@%s:%d/%s'%(
            "oracrad",
            "Hm4CeqH7hkUf",
            "nas3",
            3307,
            "OracRad"
            )


class MQTTGroupTests(unittest.TestCase):
    
    def testGroup(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        
        group = MQTTGroup("ALL")
        res = group.getGroupTwinIds(s)
        self.assertGreater(len(res), 0)
        
    def testEmptyGroup(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        
        group = MQTTGroup("UNKNOWN")
        res = group.getGroupTwinIds(s)
        self.assertEqual(len(res), 0)
        
   
        
if __name__ == '__main__':
    unittest.main()