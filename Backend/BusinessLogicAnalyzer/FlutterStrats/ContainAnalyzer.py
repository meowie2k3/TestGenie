from ..Diagram.Block import Block, BlockType
from ..Diagram.Connection import Connection, ConnectionType
import os

def ContainAnalyzer(diagram, block, visited = []):
    visited.append(block)
    currType = block.type
    
    # print("Current content: ", currContent)
    # print("Current type: ", currType)
    
    # keep analyze unless the block is a function or global variable
    if (currType != BlockType.FUNCTION and currType != BlockType.GLOBAL_VAR):
        content = block.getContentNoComment()
        # print(content)
        lines = content.split('\n')
        # if type is file, analyze classes and functions (standalone functions)
        # if type is class, analyze functions
        blocks = []
        if (currType == BlockType.FILE):
            # two cases: class and abstract class
            if 'class ' in content:
                # this file have class(es)
                isClassContent = False
                openedBracket = 0
                className = ''
                classContent = []
                # class
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
                        if openedBracket > 0:
                            openedBracket = openedBracket - 1
                        else: 
                            # class end
                            isClassContent = False
                            classContent = '\n'.join(classContent)
                            blocks.append(Block(className, classContent, BlockType.CLASS))
                            classContent = []
                    elif '{' in line and isClassContent:
                        openedBracket = openedBracket + 1
                        classContent.append(line)
                    elif isClassContent:
                        classContent.append(line)
                
                # abstract class
                if 'abstract class ' in content:
                    isAbstractClassContent = False
                    openedBracket = 0
                    className = ''
                    classContent = []
                    for line in lines:
                        if line.strip().startswith('abstract class '):
                            # first line of class
                            # NOTE: there is no class inside class
                            # get class name
                            className = line.split('abstract class ')[1].split('{')[0].strip()
                            # print(className)
                            isAbstractClassContent = True
                            classContent.append(line)
                        elif '}' in line and isAbstractClassContent:
                            # two cases: class end or function end
                            classContent.append(line)
                            if '{' in line:
                                continue
                            if openedBracket > 0:
                                openedBracket = openedBracket - 1
                            else: 
                                # class end
                                isAbstractClassContent = False
                                classContent = '\n'.join(classContent)
                                blocks.append(Block(className, classContent, BlockType.ABSTRACT_CLASS))
                                classContent = []
                        elif '{' in line and isAbstractClassContent:
                            openedBracket = openedBracket + 1
                            classContent.append(line)
                        elif isAbstractClassContent:
                            classContent.append(line)
                            
            # enum
            if 'enum ' in content:
                # no {} in enum
                # maybe () in enum
                # once } is found, enum end
                isEnumContent = False
                enumName = ''
                enumContent = []
                for line in lines:
                    if line.strip().startswith('enum '):
                        # first line of enum
                        enumName = line.split('enum ')[1].split('{')[0].strip()
                        isEnumContent = True
                        enumContent.append(line)
                    elif '}' in line and isEnumContent:
                        enumContent.append(line)
                        isEnumContent = False
                        enumContent = '\n'.join(enumContent)
                        blocks.append(Block(enumName, enumContent, BlockType.ENUM))
                    elif isEnumContent:
                        enumContent.append(line)
                
            # function
            # standalone function / GlobalVar only!
            # strat: get rid of all analyzed class and enum first
            leftoverContent = content
            for b in blocks:
                leftoverContent = leftoverContent.replace(b.content, '')
            print(block.name)
            print(leftoverContent)
                    

                         
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
    
    