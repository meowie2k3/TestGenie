
class _BlocType:
    MAIN = 'Main'
    CLASS = 'Class'
    FUNCTION = 'Function'
    
class Block:
    
    def __init__(self, name, content):
        self.name = name
        self.content = content
        self.type = self.__getBlockType()
        # self.prediction = self.__predict()
        
    def __getBlockType(self) -> _BlocType:
        # TODO: Implement the logic to determine the type of the block
        return _BlocType.MAIN
    
    def __predict(self):
        return ''
    
    def getPrediction(self):
        return self.prediction