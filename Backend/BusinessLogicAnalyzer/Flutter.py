from .Diagram.Block import Block
from .Diagram.Connection import Connection

def FlutterAnalyzeStrategy(diagram) -> None:
    # print('Flutter analyze strategy')
    # print(diagram)
    fileList = diagram.project.getListSourceFiles()
    # print(fileList)
    # create a block for main first
    mainfile = fileList[0]
    mainBlock = Block(mainfile, diagram.project.getFileContent(mainfile))
    # print(mainBlock)
    _ImportAnalyzer(diagram, mainBlock)
    pass


def _ImportAnalyzer(diagram, block):
    currContent = block.content
    currType = block.type
    # print("Current content: ", currentContent)
    # print("Current type: ", currentType)
    
    # analyze imports
    if (currType == 'file'):
        importLines = [line.strip() for line in currContent.split('\n') if line.strip().startswith('import')]
        # print(importLines)
        for line in importLines:
            # print(line)
            directory = line.split(' ')[1].replace(';', '')
            print(directory)
            