
class BlockType:
    FILE = 'File'
    CLASS = 'Class'
    FUNCTION = 'Function'
    
class Block:
    
    def __init__(self, name: str, content: str, type:str):
        self.name = name
        self.content = content
        self.type = type
        
    def __predict(self):
        return ''
    
    def predict(self):
        self.prediction = self.__predict()
    
    def getPrediction(self):
        return self.prediction
    
    def __str__(self):
        return f'{self.name} - {self.type}'