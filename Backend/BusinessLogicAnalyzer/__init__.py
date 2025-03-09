from ProjectManager import Project
from .Diagram import Block, Connection
from .Flutter import FlutterAnalyzeStrategy
import sqlite3

class DependencyDiagram:
    
    blocks = []
    connections = []
    
    def __init__(self, project: Project) -> None:
        self.project = project
        self._generateDiagram()
        # generate db for diagram
        self._generateDB()
        
    def _generateDiagram(self) -> None:
        # Analyze project abstractly to project's framework
        framework = self.project.getFramework()
        functionName = framework + 'AnalyzeStrategy'
        if functionName in globals():
            globals()[functionName](self)
        else:
            raise Exception('Framework not supported')
        
    def _generateDB(self) -> None:
        # create db folder if not exist
        import os
        if not os.path.exists('db'):
            os.makedirs('db')
        filename = f'{self.project.getName()}.db' 
        # create a connection to the database
        self.connection = sqlite3.connect(f'db/{filename}')
    
        # schema
        cursor = self.connection.cursor()
        # type
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ConnectionType (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS BlockType (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            )
        ''')
        # insert type
        blockTypeList = Block.getAllTypes()
        connectionTypeList = Connection.getAllTypes()
        for blockType in blockTypeList:
            cursor.execute('''
                INSERT INTO BlockType (name) VALUES (?)
            ''', (blockType,))
        for connectionType in connectionTypeList:
            cursor.execute('''
                INSERT INTO ConnectionType (name) VALUES (?)
            ''', (connectionType,))
        
        # connection and block
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Block (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                content TEXT,
                prediction TEXT,
                type_id INTEGER,
                FOREIGN KEY(type_id) REFERENCES BlockType(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Connection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                head_id INTEGER,
                tail_id INTEGER,
                type_id INTEGER,
                FOREIGN KEY(head_id) REFERENCES Block(id),
                FOREIGN KEY(tail_id) REFERENCES Block(id),
                FOREIGN KEY(type_id) REFERENCES ConnectionType(id)
            )
        ''')
        # insert block and connection
        for block in self.blocks:
            # NOTE: type_id is interger and FK to BlockType
            cursor.execute('''
                INSERT INTO Block (name, content, prediction, type_id) VALUES (?, ?, ?, ?)
            ''', (block.name, block.content, block.prediction, block.type))
            
        for connection in self.connections:
            # NOTE: head, tail are block id from Block table
            # type_id is interger and FK to ConnectionType
            cursor.execute('''
                INSERT INTO Connection (head_id, tail_id, type_id) VALUES (?, ?, ?)
            ''', (connection.head, connection.tail, connection.type))
            
            
            
        
        
    def __str__(self) -> str:
        """_summary_

        Returns:
            str: project name, list of blocks and connections in the diagram
        """
        res = f'Project: {self.project.getName()}\n'
        res += 'Blocks:\n'
        for block in self.blocks:
            res += f'{block.name} - {block.type}\n'
        res += 'Connections:\n'
        for connection in self.connections:
            res += f'{connection.head.name} -> {connection.tail.name} - {connection.type}\n'
        return res
        