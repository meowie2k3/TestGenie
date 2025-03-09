from .Block import Block

class ConnectionType:
    EXTEND = 'Extend'
    IMPLEMENT = 'Implement'
    CONTAIN = 'Contain'
    EXTEND = 'Extend'
    USE = 'Use'
    CALL = 'Call'
    IMPORT = 'Import'
    
    def getAllTypes():
        return [ConnectionType.EXTEND, ConnectionType.IMPLEMENT, ConnectionType.CONTAIN, ConnectionType.EXTEND, ConnectionType.USE, ConnectionType.CALL, ConnectionType.IMPORT]

class Connection:
    def __init__(self, head: Block, tail: Block, type: str):
        self.head = head
        self.tail = tail
        self.type = type
        
    def __str__(self):
        return f'{self.head} --> {self.tail} --- {self.type}'
        