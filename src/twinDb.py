#===============================================================================
# TwinDb - Extension of Twin model of thing to be able to save data to DB
# Jon Durrant
# 11-Jan-2021
#===============================================================================

from twin import Twin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column
from sqlalchemy.sql.sqltypes import Boolean, String, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

class TwinDb(Twin):
    
    def __init__(self, clientId: str, options: dict = {}):
        super().__init__(options)
        self.clientId = clientId
        
    def getClientId(self):
        return self.clientId
    
    def updateDb(self, session):
        twin = TwinTable(clientId=self.clientId, 
                  reported = self.getReportedState(),
                  reportedMeta = self.getReportedMeta(),
                  desired = self.getDesiredState(),
                  desiredMeta = self.getDesiredMeta(),
                  declined = self.getDeclinedState(),
                  declinedMeta = self.getDeclinedMeta()
            )
        session.merge(twin)
        session.commit()
        return 
    
    def loadFromDb(self, session):
        try:
            twin = session.query(TwinTable).filter(TwinTable.clientId==self.clientId).one()
            self.reported.setState(twin.reported)
            self.reported.meta = twin.reportedMeta
            self.desired.setState(twin.desired)
            self.desired.meta = twin.desiredMeta
            self.declined.setState(twin.declined)
            self.declined.meta = twin.declinedMeta 
            return True
        except NoResultFound:
            return False
    
    def getTwinCount(self, session):
        try:
            count = session.query(TwinTable).count()
            return count
        except NoResultFound:
            return 0
        
    def outputJson(self, s):
        #Nop
        return
        
    
Base = declarative_base()
    
class TwinTable(Base):
    __tablename__ = 'twin'

    clientId        = Column(String, primary_key=True)
    reported        = Column(JSON)
    reportedMeta    = Column(JSON)
    desired         = Column(JSON)
    desiredMeta     = Column(JSON)
    declined        = Column(JSON)
    declinedMeta    = Column(JSON)

    def __repr__(self):
       return "<Twin(clientId='%s', reported='%s', reportedMeta='%s', desired='%s', desiredMeta='%s', rejected=%d, rejectedMeta=%s)>" % (
            self.clientId, self.reported, self.reportedMeta, self.desired, self.desiredMeta, self.rejected, self.rejectedMeta)






'''
CREATE TABLE twin( 
  clientId varchar(80) primary key, 
  reported json,
  reportedMeta json,
  desired json,
  desiredMeta json,
  declined json,
  declinedMeta json
);
'''