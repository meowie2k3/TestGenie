from .Diagram.Block import Block, BlockType

from .FlutterStrats.ImportAnalyzer import ImportAnalyzer
from .FlutterStrats.ContainAnalyzer import ContainAnalyzer
from .FlutterStrats.CallAnalyzer import CallAnalyzer
# from LLMService import LLM

def FlutterAnalyzeStrategy(diagram) -> None:
    # print('Flutter analyze strategy')
    # print(diagram)
    fileList = diagram.project.getListSourceFiles()
    # print(fileList)
    # create a block for main first
    mainfileDir = fileList[0]
    mainFileContent = diagram.project.getFileContent(mainfileDir)
    mainBlock = Block(mainfileDir, mainFileContent, BlockType.FILE)
    # print(mainBlock)
    
    # llm = LLM(model='deepseek-r1-distill-llama-8b', purpose='Analyzing Flutter project into dependency diagram')
    # question = "What are the imports in the main file?\n" + mainFileContent
    # res = llm.invoke(question)
    # F word to the LLM
    diagram.blocks.append(mainBlock)
    
    ImportAnalyzer(diagram, diagram.blocks[0])
    
    ContainAnalyzer(diagram, diagram.blocks[0])
    
    CallAnalyzer(diagram, diagram.blocks[0])
    
    print("===============Analyzing result===============")
    for block in diagram.blocks:
        print(block)
        # if block.type != BlockType.FILE:
        #     print(block.getContentNoComment())
        print("=========================")
        
    for connection in diagram.connections:
        print(connection)
        print("=========================")
        



    