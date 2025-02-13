
BlockType = {
    "FILE": "file",
    "CLASS": "class",
    "FUNCTION": "function",
}
    
class Block:
    
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content
        self.type = self.__getBlockType()
        self.prediction = self.__predict()
        
    def __getBlockType(self) -> str:
        # TODO: Implement the logic to determine the type of the block
        return BlockType["FILE"]
    
    def __predict(self):
        return ''
    
    def getPrediction(self):
        return self.prediction
    
    def __str__(self):
        return f'{self.name} - {self.type}'