
class BlockType:
    FILE = 'File'
    CLASS = 'Class'
    ABSTRACT_CLASS = 'AbstractClass'
    GLOBAL_VAR = 'GlobalVar'
    ENUM = 'Enum'
    FUNCTION = 'Function'
    CLASS_FUNCTION = 'ClassFunction'
    CLASS_CONSTRUCTOR = 'ClassConstructor'
    CLASS_ATTRIBUTE = 'ClassAttribute'
    
    
class Block:
    
    def __init__(self, name: str, content: str, type:str):
        self.name = name
        self.content = content
        self.type = type
        
    def __predict(self):
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

    
    def predict(self):
        self.prediction = self.__predict()

    def getPrediction(self):
        return self.prediction
    
    def __str__(self):
        return f'{self.name} - {self.type}'
    
if __name__ == '__main__':
    content = "} /* Lmao */ /n"
    type = BlockType.FILE
    block = Block('lib/main.dart', content, type)
    print(block.getContentNoComment())