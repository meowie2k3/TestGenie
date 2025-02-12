from .Diagram.Block import Block
from .Diagram.Connection import Connection
from LLMService import LLM

def FlutterAnalyzeStrategy(diagram) -> None:
    # print('Flutter analyze strategy')
    # print(diagram)
    fileList = diagram.project.getListSourceFiles()
    # print(fileList)
    # create a block for main first
    mainfileDir = fileList[0]
    mainFileContent = diagram.project.getFileContent(mainfileDir)
    mainBlock = Block(mainfileDir, mainFileContent)
    # print(mainBlock)
    
    # llm = LLM(model='deepseek-r1-distill-llama-8b', purpose='Analyzing Flutter project into dependency diagram')
    # question = "What are the imports in the main file?\n" + mainFileContent
    # res = llm.invoke(question)
    # F word to the LLM
    
    
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
            # delete first and last character => delete quotes
            directory = directory[1:-1]
            print(directory)
            # 3 cases: import from other package, import from project, import as relative path
            if directory.startswith('package:'):
                # import from other package, import from project
                prjName = diagram.project.getName()
                pass
            