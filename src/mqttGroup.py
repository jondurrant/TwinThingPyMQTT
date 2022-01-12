#===============================================================================
# MQTTGRoup - class for query groups from MQTT ACL
#===============================================================================


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column
from sqlalchemy.sql.sqltypes import Boolean, String, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from array import array
import pandas as pd

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
        
        
    def selectTwinFrame(self, session, select: array = [], asColumn: array = [], where: dict = {}, orient: str="split"):
        sql = 'SELECT '
        selectCount = len(select)
        if (selectCount == 0):
            sql = sql + '* '
        for i in range(selectCount):
            s = self.sqlSelect(select[i])
            if (len(asColumn) > i):
                sql = sql + s + " as " + asColumn[i]
            else:
                sql = sql + s
            if (i == (selectCount -1)):
                sql = sql + " "
            else :
                sql = sql + ", "
        
        sql = sql + "FROM twin WHERE clientId in ("
        targets = self.getGroupTwinIds(session)
        targetCount = len(targets)
        for i in range(targetCount):
            target = targets[i]
            sql = sql + '"' +target + '" '
            if (i < (targetCount -1)):
                sql = sql + ", "
        sql = sql + ')'
        
        if (not where == {}):
            sql = sql + " AND (" + self.whereToSQL(where)+")"
        
        
        sql = sql + ';'
        
        
        frame = pd.read_sql(sql, session.connection())
        
        if (not orient in ["split", "records", "index", "values", "table", "columns"]):
            orient = "split"
        return frame.to_json( orient=orient)
    
    
    
    
    def sqlSelect(self, column: str):
        parts = column.split(".", 1)
        if (len(parts) == 1):
            return parts[0]
        else:
            return ("json_extract(%s, \'$.%s\')"%(parts[0], parts[1]))


    def whereToSQL(self, where: dict):
        res=""
        if ("column" in where):
            if (("op" in where) and ("value" in where)):
                res = "%s %s %s"%(
                    self.sqlSelect(where["column"]),
                    where["op"],
                    self.sqlLiteral(where["value"])
                    )
        if ("and" in where):
            count = len(where["and"])
            if (count > 0):
                res = "("
                for i in range(count):
                    res = res + self.whereToSQL(where["and"][i])
                    if (i < (count -1)):
                        res = res + " AND "
                res = res + ")"
        if ("or" in where):
            count = len(where["or"])
            if (count > 0):
                res = "("
                for i in range(count):
                    res = res + self.whereToSQL(where["or"][i])
                    if (i < (count -1)):
                        res = res + " OR "
                res = res + ")"
        return res
        
    def sqlLiteral(self, o):
        if (isinstance(o, str)):
            return '"%s"'%o
        elif (isinstance(o, int)):
            return '%d'%o
        elif (isinstance(o, float)):
            return '%f'%o
        else:
            return ""+o
        