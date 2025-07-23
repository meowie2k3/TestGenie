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
        if not self._isProjectExistInDB():
            self._insertProject()
            
        else:
            # TODO: do something if project already exist
            self.projectId = self.getProjectId()
            pass
        
    
    def getJsonDiagram(self) -> dict:
        """
        Get the diagram in json format
        Dict structure:
        {
            project: "project_name",
            blocks: [
                {
                    id: 1,
                    name: "block_name",
                    content: "block_content",
                    prediction: "block_prediction",
                    type: "block_type"
                }
            ]
            connections: [
                {
                    head: 1,
                    tail: 2,
                    type: "connection_type"
                }
            ]
        }
        """
        # fetch diagram from db
        blockQuery = Block.getTable().getSelectSQL(fields=['id','name','type'],conditions={
            'project_id': self.projectId
        })
        blocks = self.execute(blockQuery)

        connectionQuery = Connection.getTable().getSelectSQL(fields=['id','head','tail','type'], conditions={
            'project_id': self.projectId
        })
        connections = self.execute(connectionQuery)
        
        # print(blocks)
        # print(connections)
        
        res = {
            'project': self.project.getName(),
            'blocks': [],
            'connections': []
        }
        for block in blocks:
            res['blocks'].append({
                'id': block[0],
                'name': block[1],
                'type': self._getEnumName('BlockType', block[2]),
            })
            
        for connection in connections:
            res['connections'].append({
                'head': connection[1],
                'tail': connection[2],
                'type': self._getEnumName('ConnectionType', connection[3])
            })
            
        return res
        
        pass
    
    def getProjectId(self) -> int:
        query = self.project.getTable().getSelectSQL(fields=['id'], conditions={
            'name': self.project.getName()
        })
        res = self.execute(query)
        if len(res) == 0:
            return -1
        return res[0][0]
    
    def getBlockName(self, blockId: int) -> str:
        query = Block.getTable().getSelectSQL(fields=['name'], conditions={
            'id': blockId
        })
        res = self.execute(query)
        return res[0][0]
    
    def getBlockContent(self, blockId: int) -> str:
        query = Block.getTable().getSelectSQL(fields=['content'], conditions={
            'id': blockId
        })
        res = self.execute(query)
        return res[0][0]

    def getBlockPrediction(self, blockId: int) -> str:
        query = Block.getTable().getSelectSQL(fields=['prediction'], conditions={
            'id': blockId
        })
        res = self.execute(query)
        return res[0][0]
    
    def getBlockOriginal(self, blockId: int, connectionIds = []) -> list[int]:
        # take blockId as tail, query connection table to get head
        # backtracking until reach FILE block type and return the blockname
        # print('blockId:', blockId)
        query = Connection.getTable().getSelectSQL(fields=['id', 'head', 'type'], conditions={
            'tail': blockId
        })
        res = self.execute(query)
        for row in res:
            connectionType = self._getEnumName('ConnectionType', row[2])
            if connectionType == ConnectionType.CALL or connectionType == ConnectionType.USE:
                continue
            
            connectionId = row[0]
            connectionIds.append(connectionId)
            
            headBlockId = row[1]
            
            headblockQuery = Block.getTable().getSelectSQL(fields=['type'], conditions={
                'id': headBlockId
            })
            headblock = self.execute(headblockQuery)
            # print(headblock)
            headBlockType = self._getEnumName('BlockType', headblock[0][0])
            if headBlockType == BlockType.FILE:
                return connectionIds
            return self.getBlockOriginal(headBlockId,  connectionIds)
        return connectionIds
            
    def getBlockFromId(self, blockId: int) -> Block:
        query = Block.getTable().getSelectSQL(fields=['name', 'content', 'type'], conditions={
            'id': blockId
        })
        res = self.execute(query)
        if len(res) == 0:
            return None
        row = res[0]
        blockType = self._getEnumName('BlockType', row[2])
        return Block(row[0], row[1], blockType)
    
    def getConnectionFromId(self, connectionId: int) -> Connection:
        query = Connection.getTable().getSelectSQL(fields=['head', 'tail', 'type'], conditions={
            'id': connectionId
        })
        res = self.execute(query)
        if len(res) == 0:
            return None
        row = res[0]
        headBlock = self.getBlockFromId(row[0])
        tailBlock = self.getBlockFromId(row[1])
        connectionType = self._getEnumName('ConnectionType', row[2])
        return Connection(headBlock, tailBlock, connectionType)
    
    def updateBlockPrediction(self, blockId: int, prediction: str) -> None:
        query = Block.getTable().getUpdateSQL(
            values={
                'prediction': self._handldApostropheString(prediction)
            },
            conditions={
                'id': blockId
            }
        )
        self.execute(query)
        
        pass    
        
    def _connect(self):
        from dotenv import load_dotenv
        import os
        if load_dotenv(override=True) == False:
            raise Exception("Failed to load .env file")
        self.connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
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
        return self.cursor.fetchall() # type: ignore
    
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
        query = self.project.getTable().getSelectSQL(fields=['name'], conditions={
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
        # print(query)
        self.execute(query)
        # diagram insert
        diagram = DependencyDiagram(self.project)
        # not sure if this is needed
        self.diagram = diagram
        self.projectId = self.getProjectId()
        
        blocks = diagram.blocks
        connections = diagram.connections
        self._mapBlocksIntoDB(blocks)
        self._mapConnectionsIntoDB(connections)
        
    
    def _mapBlocksIntoDB(self, blocks: list):
        for block in blocks:
            # TODO: handle apostrophe in content
            # map into block table
            query = Block.getTable().getInsertSQL({
                'name': self._handldApostropheString(block.name),
                'project_id': self.projectId,
                'content': self._handldApostropheString(block.content),
                'prediction': self._handldApostropheString(block.prediction),
                'type': self._getEnumId('BlockType', block.type)
            })
            self.execute(query)
        pass
    
    def _mapConnectionsIntoDB(self, connections: list):
        for connection in connections:
            # map into connection table
            query = Connection.getTable().getInsertSQL({
                'head': self._getBlockId(connection.head),
                'tail': self._getBlockId(connection.tail),
                'type': self._getEnumId('ConnectionType', connection.type),
                'project_id': self.projectId
            })
            self.execute(query)
        pass
    
    def _getBlockId(self, block) -> int:
        table = Block.getTable()
        query = table.getSelectSQL(fields=['id'], conditions={
            'name': self._handldApostropheString(block.name),
            'project_id': self.projectId,
            'content': self._handldApostropheString(block.content),
            'prediction': self._handldApostropheString(block.prediction),
            'type': self._getEnumId('BlockType', block.type)
        })
        res = self.execute(query)
        return res[0][0]
    
    def _getEnumId(self, enum, enumName: str) -> int:
        # base on enumname to get blocktype or connectiontype id
        if enum in globals():
            enumClass = globals()[enum]
            table = enumClass.getTable()
            query = table.getSelectSQL(fields=['id'], conditions={
                'name': enumName
            })
            res = self.execute(query)
            return res[0][0]
        return 0
    
    def _getEnumName(self, enum, enumId: int) -> str:
        if enum in globals():
            enumClass = globals()[enum]
            table = enumClass.getTable()
            query = table.getSelectSQL(fields=['name'], conditions={
                'id': enumId
            })
            res = self.execute(query)
            return res[0][0]
        return ''
    
    def _handldApostropheString(self, string: str) -> str:
        return string.replace("'", "''")
        pass
    