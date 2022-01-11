import unittest
from twinDb import TwinDb
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


connectStr='mysql+pymysql://%s:%s@%s:%d/%s'%(
            "oracrad",
            "Hm4CeqH7hkUf",
            "nas3",
            3307,
            "OracRad"
            )


class TwinDbTests(unittest.TestCase):
    
    def testStore(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        twin = TwinDb("foo")
        twin.stateFromThing({
            "trn":1,
            "count": 22
            })
        twin.updateDb(s)
        
        
    def testLoad(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        twin = TwinDb("jon")
        twin.stateFromThing({
            "trn":1,
            "count": 23
            })
        twin.updateDb(s)
        
        twin2 = TwinDb("jon")
        self.assertEqual(twin2.loadFromDb(s), True)
        state = twin2.getReportedState()
        self.assertEqual(state["count"], 23)
        
        
    def testLoadUnknown(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        twin = TwinDb("unknown")
        twin.stateFromThing({
            "trn":1,
            "count": 13
            })
        self.assertEqual(twin.loadFromDb(s), False)
        state = twin.getReportedState()
        self.assertEqual(state["count"], 13)
        
        
if __name__ == '__main__':
    unittest.main()