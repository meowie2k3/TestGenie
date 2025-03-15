from BusinessLogicAnalyzer import DependencyDiagram
from BusinessLogicAnalyzer.Diagram.Block import Block, BlockType
from BusinessLogicAnalyzer.Diagram.Connection import Connection, ConnectionType
import mysql.connector

class DBMS:
    
    _numberOfTables = 5
    
    def __init__(self, project) -> None:
        self.project = project

        # print(self._isDBinit())
        if not self._isDBinit():
            self._initDB()
        
        # print(self._isProjectExistInDB())
        # if not self._isProjectExistInDB():
        self._insertProject()
        
        
    def _connect(self):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='test_genie'
        )
        self.cursor = self.connection.cursor(buffered=True)
        
    def _close(self):
        self.cursor.close()
        self.connection.close()
        
    def _isDBinit(self):
        query = 'SHOW TABLES'
        res = self.execute(query)
        return len(res) >= self._numberOfTables
    
    def execute(self, query) -> list:
        self._connect()
        
        if type(query) == str:
            self.cursor.execute(query)
        else:
            for q in query:
                self.cursor.execute(q)
        self.connection.commit()
        
        self._close()
        return self.cursor.fetchall()
    
    def _initDB(self):
        projectQuery = self.project.getTable().getCreateSQL()
        self.execute(projectQuery)
        
        blockCreateQuery = Block.getTable().getCreateSQL()
        self.execute(blockCreateQuery)
        
        connectionQuery = Connection.getTable().getCreateSQL()
        self.execute(connectionQuery)
        self._insertEnumDB()
        
    def _insertEnumDB(self):
        
        blockTypeCreateQuery = BlockType.getTable().getCreateSQL()
        # print(blockTypeQuery)
        self.execute(blockTypeCreateQuery)
        
        blockTypeInsertQuery = BlockType.getInsertQuery()
        # print(blockTypeInsertQuery)
        self.execute(blockTypeInsertQuery)
        
        connectionTypeCreateQuery = ConnectionType.getTable().getCreateSQL()
        self.execute(connectionTypeCreateQuery)
        
        connectionTypeInsertQuery = ConnectionType.getInsertQuery()
        # print(connectionTypeInsertQuery)
        self.execute(connectionTypeInsertQuery)
    
    def _isProjectExistInDB(self):
        query = self.project.getTable().getSelectSQL({
            'name': self.project.getName()
        })
        # print(query)
        res = self.execute(query)
        return len(res) > 0
    
    def _insertProject(self):
        # print('Inserting project')
        # project table insert
        query = self.project.getTable().getInsertSQL({
            'name': self.project.getName(),
            'directory': self.project.getPath()
        })
        print(query)
        # self.execute(query)
        # diagram insert
        diagram = DependencyDiagram(self.project)
        blocks = diagram.blocks
        connections = diagram.connections
        for block in blocks:
            type = block.type
            
            pass
        pass
    
    def _getEnumId(self, enum, enumName: str):
        pass
    
    