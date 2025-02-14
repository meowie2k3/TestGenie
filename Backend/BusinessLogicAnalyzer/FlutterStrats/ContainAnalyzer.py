from ..Diagram.Block import Block, BlockType
from ..Diagram.Connection import Connection, ConnectionType
import os

def ContainAnalyzer(diagram, block, visited = []):
    visited.append(block)
    currType = block.type
    
    # print("Current content: ", currContent)
    # print("Current type: ", currType)
    
    # keep analyze unless the block is a function
    if (currType != 'Function'):
        content = block.getContentNoComment()
        # print(content)
        lines = content.split('\n')
        # if type is file, analyze classes and functions (standalone functions)
        # if type is class, analyze functions
        blocks = []
        if (currType == 'File'):
            # two cases: class and abstract class
            # class
            if 'class' in content:
                # this file have class(es)
                isClassContent = False
                isOpeningBracket = False
                className = ''
                classContent = []
                for line in lines:
                    if line.strip().startswith('class '):
                        # first line of class
                        # NOTE: there is no class inside class
                        # get class name
                        className = line.split('class ')[1].split('{')[0].strip()
                        # print(className)
                        isClassContent = True
                        classContent.append(line)
                    elif '}' in line and isClassContent:
                        # two cases: class end or function end
                        classContent.append(line)
                        if '{' in line:
                            continue
                        if isOpeningBracket:
                            isOpeningBracket = False
                        else: 
                            # class end
                            isClassContent = False
                            classContent = '\n'.join(classContent)
                            blocks.append(Block(className, classContent, BlockType.CLASS))
                            classContent = []
                    elif '{' in line and isClassContent:
                        isOpeningBracket = True
                        classContent.append(line)
                    elif isClassContent:
                        classContent.append(line)

                         
        for b in blocks:
            # print(b)
            # print(b.content)
            diagram.blocks.append(b)
            diagram.connections.append(Connection(block, b, ConnectionType.CONTAIN))
            ContainAnalyzer(diagram, b, visited=visited)
            
        # find connection connected to this block and not visited
    connectedBlocks = [c.tail for c in diagram.connections if c.head == block and c.tail not in visited]
    for b in connectedBlocks:
        ContainAnalyzer(diagram, b, visited=visited)    
    
    