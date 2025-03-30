
class BlockType:
    FILE = 'File'
    CLASS = 'Class'
    ABSTRACT_CLASS = 'AbstractClass'
    ENUM = 'Enum'
    GLOBAL_VAR = 'GlobalVar'
    FUNCTION = 'Function'
    CLASS_CONSTRUCTOR = 'ClassConstructor'
    CLASS_FUNCTION = 'ClassFunction'
    CLASS_ATTRIBUTE = 'ClassAttribute'
    
    @staticmethod
    def getInsertQuery()->list[str]:
        # return attributes of this class
        attList = [attr for attr in dir(BlockType) if not callable(getattr(BlockType, attr)) and not attr.startswith("__")]
        table = BlockType.getTable()
        query = []
        for att in attList:
            query.append( table.getInsertSQL({'name': getattr(BlockType, att)}) + ';')
            
        return query
    
    @staticmethod
    def getTable():
        from DBMS.Table import Table
        return Table(
            'BlockType',
            {
                'id': 'INT AUTO_INCREMENT PRIMARY KEY',
                'name': 'VARCHAR(255)'
            }
        )
    
    
class Block:
    
    def __init__(self, name: str, content: str, type: str) -> None:
        self.name = name
        self.content = content
        self.type = type
        self.predict()
        
    def __predict(self) -> str:
        # TODO: implement prediction
        return ''
    
    def getContentNoComment(self) -> str:
        # no split by line
        content = self.content
        res = ''
        i = 0
        isCommentSingleLine = False
        isCommentMultiLine = False
        while i < len(self.content)-1:
            # if \n, reset isCommentSingleLine
            if content[i] == '\n':
                isCommentSingleLine = False
            if content[i] == '/' and content[i+1] == '*':
                isCommentMultiLine = True
            if content[i] == '/' and content[i+1] == '/':
                isCommentSingleLine = True
            if not isCommentSingleLine and not isCommentMultiLine:
                res += content[i]
            if content[i] == '*' and content[i+1] == '/':
                isCommentMultiLine = False
                i+=1
            i+=1
        
        # delete all empty lines
        res = '\n'.join([line for line in res.split('\n') if line.strip() != ''])
        
        return res

    
    def predict(self) -> None:
        self.prediction = self.__predict()

    def getPrediction(self) -> str:
        return self.prediction
    
    @staticmethod
    def getTable():
        from DBMS.Table import Table
        return Table(
            'Block',
            {
                'id': 'INT AUTO_INCREMENT PRIMARY KEY',
                'name': 'VARCHAR(255)',
                'content': 'TEXT',
                'prediction': 'TEXT',
                'type': 'INT',
                '': 'FOREIGN KEY (type) REFERENCES BlockType(id)'
            }
        )
    
    def __str__(self):
        return f'{self.name} - {self.type}'
    
    
if __name__ == '__main__':
    content = "} /* Lmao */ /n"
    type = BlockType.FILE
    block = Block('lib/main.dart', content, type)
    print(block.getContentNoComment())