#===============================================================================
# MQTTGRoup - class for query groups from MQTT ACL
#===============================================================================


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column
from sqlalchemy.sql.sqltypes import Boolean, String, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

class MQTTGroup:
    def __init__(self, name: str):
        self.name = name
        
    def getGroupTwinIds(self, session):
        con = session.connection()
        rs = con.execute('SELECT DISTINCT clientid FROM mqtt_acl where topic = "GRP/%s/#";'%self.name)
        res = []
        for row in rs:
            res.append(row[0])
        return res
        
        
        
