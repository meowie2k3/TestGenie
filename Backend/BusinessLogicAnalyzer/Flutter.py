from .Diagram.Block import Block
from .Diagram.Connection import Connection

def FlutterAnalyzeStrategy(diagram) -> None:
    # print('Flutter analyze strategy')
    # print(diagram)
    fileList = diagram.project.getListSourceFiles()
    print(fileList)
    # create a block for main first
    
    pass