from ..Diagram.Block import Block
from ..Diagram.Connection import Connection, ConnectionType
import os

def ImportAnalyzer(diagram, block):
    currContent = block.content
    currType = block.type
    # print("Current content: ", currentContent)
    # print("Current type: ", currentType)
    
    # analyze imports
    if (currType == 'file'):
        importLines = [line.strip() for line in currContent.split('\n') if line.strip().startswith('import')]
        # print(importLines)
        blocks = []
        for line in importLines:
            # print(line)
            directory = line.split(' ')[1].replace(';', '')
            # delete first and last character => delete quotes
            directory = directory[1:-1]
            # print(directory)
            # 3 cases: import from other package, import from project, import as relative path
            if directory.startswith('package:'):
                # import from other package, import from project
                prjName = diagram.project.yaml_name
                if directory.startswith(f'package:{prjName}'):
                    # import from project
                    # create block for this file and connection
                    fileDir = directory.split(f'package:{prjName}')[1]
                    fileDir = 'lib' + fileDir
                    fileContent = diagram.project.getFileContent(fileDir)
                    # if fileDir is not in Diagram.blocks
                    if not any(block.name == fileDir for block in diagram.blocks):
                        blocks.append(Block(fileDir, fileContent))
                    else: diagram.connections.append(Connection(block, [b for b in diagram.blocks if b.name == fileDir][0], ConnectionType.IMPORT))
            else:
                # import as relative path
                currentDir = block.name #ex: lib/main.dart
                currentDir = currentDir.split('/')
                currentDir.pop()
                currentDir = '/'.join(currentDir)
                combineDir = os.path.normpath(os.path.join(currentDir, directory))
                # print(combineDir)
                fileContent = diagram.project.getFileContent(combineDir)
                if combineDir not in [block.name for block in diagram.blocks]:
                    blocks.append(Block(combineDir, fileContent))
                else: diagram.connections.append(Connection(block, [b for b in diagram.blocks if b.name == combineDir][0], ConnectionType.IMPORT))
        
        for b in blocks:
            # print(b)
            diagram.blocks.append(b)
            diagram.connections.append(Connection(block, b, ConnectionType.IMPORT))
            ImportAnalyzer(diagram, b)
            
    
