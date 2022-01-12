import unittest
from mqttGroup import MQTTGroup
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pandas as pd
import json


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
        s.close()
        
    def testEmptyGroup(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        
        group = MQTTGroup("UNKNOWN")
        res = group.getGroupTwinIds(s)
        self.assertEqual(len(res), 0)
        s.close()
        
    def foo(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        
        sql = 'select * from twin where clientId in ("BCFF4D195C03", "BCFF4D197AE6") and reported.temp > 23.0'
        sql = 'SELECT clientId,  json_extract(reported, \'$.temp\')  FROM OracRad.twin '  
        sql = sql +  'where clientId in ("BCFF4D195C03", "BCFF4D197AE6") and ' 
        sql = sql +  'json_extract(reported, \'$.temp\') > 25.0;'
        frame = pd.read_sql(sql, s.connection())
        print(frame)
        s.close()
        
    def testGroupSelect(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        
        group = MQTTGroup("saber")
        j = group.selectTwinFrame(s, ["clientId"], [])
        d = json.loads(j)
        self.assertEqual(len(d["columns"]), 1)
        self.assertEqual(d["columns"][0], "clientId")
        self.assertGreater(len(d["data"]), 2)
        #print(json.dumps(d, indent=4))
        s.close()
        
    def testGroupSelectAs(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        
        group = MQTTGroup("saber")
        j = group.selectTwinFrame(s, ["clientId"], ["id"])
        d = json.loads(j)
        self.assertEqual(len(d["columns"]), 1)
        self.assertEqual(d["columns"][0], "id")
        self.assertGreater(len(d["data"]), 2)
        #print(json.dumps(d, indent=4))
        s.close()
          
    def testGpSelectJson(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        
        group = MQTTGroup("saber")
        j = group.selectTwinFrame(s, ["clientId", "reported.temp"], ["id", "temp"], orient="split")
        d = json.loads(j)
        self.assertEqual(len(d["columns"]), 2)
        self.assertEqual(d["columns"][0], "id")
        self.assertEqual(d["columns"][1], "temp")
        self.assertGreater(len(d["data"]), 2) 
        s.close()
        
    def testGpSelectWhere(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        
        group = MQTTGroup("saber")
        where = { "column": "reported.temp", "op": ">", "value": 5.0 }
        
        j = group.selectTwinFrame(s, ["clientId", "reported.temp"], ["id", "temp"], where, "records")
        d = json.loads(j)
        self.assertGreater(len(d), 0)
        #print(json.dumps(d, indent=4))  
        s.close()   
        
    def testGpSelectWhereAnd(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        
        group = MQTTGroup("saber")
        where = {
            "and": [
                { "column": "reported.temp", "op": ">", "value": 5.0 },
                { "column": "reported.dseq", "op": "=", "value": 4 }
                ]
            }
        
        j = group.selectTwinFrame(s, ["clientId", "reported.temp", "reported.dseq"], ["id", "temp", "dseq"], where, "records")
        d = json.loads(j)
        self.assertGreater(len(d), 0)
        #print(json.dumps(d, indent=4))  
        s.close() 
        
    def testGpSelectWhereOr(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        
        group = MQTTGroup("saber")
        where = {
            "or": [
                { "column": "reported.temp", "op": ">", "value": 25.0 },
                { "column": "reported.dseq", "op": "=", "value": 3 }
                ]
            }
        
        j = group.selectTwinFrame(s, ["clientId", "reported.temp", "reported.dseq"], ["id", "temp", "dseq"], where, "records")
        d = json.loads(j)
        self.assertGreater(len(d), 0)
        #print(json.dumps(d, indent=4))  
        s.close() 
        
    def testGpSelectWhereComplex(self):
        engine = create_engine(connectStr)
        session = sessionmaker()
        session.configure(bind=engine)
        s=session()
        
        group = MQTTGroup("saber")
        where = {
            "and": [
                {"or": [
                    { "column": "reported.temp", "op": ">", "value": 25.0 },
                    { "column": "reported.dseq", "op": "=", "value": 3 }
                    ]},
                { "column": "reported.nseq", "op": "=", "value": 2 }
                ]
            }
        
        j = group.selectTwinFrame(s, ["clientId", "reported.temp", "reported.dseq"], ["id", "temp", "dseq"], where, "records")
        d = json.loads(j)
        self.assertGreater(len(d), 0)
        print(json.dumps(d, indent=4))  
        s.close() 
        
if __name__ == '__main__':
    unittest.main()