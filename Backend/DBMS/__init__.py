from BusinessLogicAnalyzer import DependencyDiagram
import mysql.connector

class DBMS:
    
    def __init__(self, project) -> None:
        # self.dependencyDiagram = DependencyDiagram(project)
        self._connect()
        print(self._isDBinit())
        
    def _connect(self):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='1234',
            database='test_genie'
        )
        self.cursor = self.connection.cursor()
        
    def _isDBinit(self):
        self.cursor.execute('SHOW TABLES')
        tables = self.cursor.fetchall()
        return len(tables) > 0
    