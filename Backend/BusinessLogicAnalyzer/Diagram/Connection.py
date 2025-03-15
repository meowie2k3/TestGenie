from .Block import Block

class ConnectionType:
    EXTEND = 'Extend'
    IMPLEMENT = 'Implement'
    CONTAIN = 'Contain'
    EXTEND = 'Extend'
    USE = 'Use'
    CALL = 'Call'
    IMPORT = 'Import'
    
    @staticmethod
    def getInsertQuery()->list[str]:
        # return attributes of this class
        attList = [attr for attr in dir(ConnectionType) if not callable(getattr(ConnectionType, attr)) and not attr.startswith("__")]
        table = ConnectionType.getTable()
        query = []
        for att in attList:
            query.append(table.getInsertSQL({'name': getattr(ConnectionType, att)}) + ';')
            
        return query
    
    @staticmethod
    def getTable():
        from DBMS.Table import Table
        return Table(
            'ConnectionType',
            {
                'id': 'INT AUTO_INCREMENT PRIMARY KEY',
                'name': 'VARCHAR(255)'
            }
        )

class Connection:
    def __init__(self, head: Block, tail: Block, type: str):
        self.head = head
        self.tail = tail
        self.type = type
    
    @staticmethod
    def getTable():
        from DBMS.Table import Table
        return Table(
            'Connection',
            {
                'id': 'INT AUTO_INCREMENT PRIMARY KEY',
                'head': 'INT',
                'tail': 'INT',
                'type': 'INT',
                '': 'FOREIGN KEY (head) REFERENCES Block(id)',
                '':'FOREIGN KEY (tail) REFERENCES Block(id)',
                '': 'FOREIGN KEY (type) REFERENCES ConnectionType(id)'
            }
        )
    
    def __str__(self):
        return f'{self.head} --> {self.tail} --- {self.type}'
        