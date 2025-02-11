from .Block import Block

class ConnectionType:
    EXTEND = 'Extend'
    IMPLEMENT = 'Implement'
    CONTAIN = 'Contain'
    USE = 'Use'
    CALL = 'Call'
    

class Connection:
    def __init__(self, head: Block, tail: Block):
        self.head = head
        self.tail = tail
        self.type = self.__getConnectionType()
        
    def __getConnectionType(self) -> ConnectionType:
        # TODO: Implement the logic to determine the type of the connection
        return ConnectionType.CALL