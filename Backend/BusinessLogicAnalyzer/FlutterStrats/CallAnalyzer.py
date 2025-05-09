from ..Diagram.Block import Block, BlockType
from ..Diagram.Connection import Connection, ConnectionType
import os
import re

def CallAnalyzer(diagram, block, visited = []):
    if block in visited:
        return
    
    visited.append(block)
    currType = block.type
    
    # NOTE strat: 2-layer recursive
    if currType in (BlockType.FILE):
        # find connected file (imported file)
        connectedFiles = [conn.tail for conn in diagram.connections if conn.head == block and conn.type == ConnectionType.IMPORT]
        
        for file in connectedFiles:
            # print("Imported file:")
            # print(file)
            # find all class/function/variable in file. Avoid BlockType.FILE
            connectedBlocks = [conn.tail for conn in diagram.connections if conn.head == file and conn.type == ConnectionType.CONTAIN]
            currentBlocks = [conn.tail for conn in diagram.connections if conn.head == block and conn.type == ConnectionType.CONTAIN]

        
            _CallAnalyzer(diagram, currentBlocks, connectedBlocks, visited)
            # import based recursive call
            CallAnalyzer(diagram, file, visited)
        
def _CallAnalyzer(diagram, thisFile, callables, visited=[]):
    # thisFile: blocks of contains in current file
    # callables: blocks of contains in imported file
    callables.extend(thisFile)
    
    # printStuff(thisFile, callables)
    
    for block in thisFile:
        if block in visited:
            continue
        
        if block.type in (BlockType.ABSTRACT_CLASS, BlockType.CLASS):
            # extend connection analyze
            name = block.name
            # print(name)
            # first word is class name
            classname = name.split()[0]
            otherInfo = name[len(classname):]
            for connBlock in callables:
                if connBlock.type in (BlockType.ABSTRACT_CLASS, BlockType.CLASS):
                    className = connBlock.name.split()[0]
                    # if className found in otherInfo, create a connection ConnectionType.EXTEND
                    if className in otherInfo:
                        diagram.connections.append(Connection(block, connBlock, ConnectionType.EXTEND))
                        # print(f"Extend connection: {block} --> {connBlock}")
                
            # split class, abstract class
            innerBlocks = [conn.tail for conn in diagram.connections if conn.head == block and conn.type == ConnectionType.CONTAIN]
            # magic recursive calls at 4 a.m
            visited.append(block)
            _CallAnalyzer(diagram, innerBlocks, callables, visited)
            
            
            continue
        else:
            visited.append(block)
            # analyze calls in block
            # If called, create a connection ConnectionType.CALL
            
            fullcontent = block.getContentNoComment()
            # print("=====================================")
            # print(block)
            # print(fullcontent)
            
            content = ''
            # Extract content only, exclude function name, params
            if block.type in (BlockType.FUNCTION, BlockType.CLASS_FUNCTION):
                if '=>' in fullcontent:
                    # take content from => to ;
                    # add a ; to the end of content
                    fullcontent = fullcontent + ';'
                    content = fullcontent[fullcontent.index('=>')+2:]
                    content = content[:content.index(';') + 1]
                
                else:
                    roundbracketOpened = 0
                    initialRoundBracket = False
                    curlybracketOpened = 0
                    isContent = False
                    for char in fullcontent:
                        # params section
                        if char == '(' and not isContent and not initialRoundBracket:
                            initialRoundBracket = True
                            roundbracketOpened += 1
                        if char == ')' and not isContent:
                            roundbracketOpened -= 1
                            if roundbracketOpened == 0 and initialRoundBracket:
                                initialRoundBracket = False
                        if char == '{':
                            if not isContent and not initialRoundBracket:
                                isContent = True
                            curlybracketOpened += 1
                        if char == '}' and isContent:
                            curlybracketOpened -= 1
                            if curlybracketOpened == 0:
                                isContent = False
                                content += char
                                break
                        if isContent:
                            content += char
            if block.type in (BlockType.CLASS_ATTRIBUTE):
                # extract content from = to ;
                # add a ; to the end of content
                fullcontent = fullcontent + ';'
                content = fullcontent[fullcontent.index('=')+1:]
                content = content[:content.index(';') + 1]
            # print("====================Block=====================")
            # print("Block name: ", block.name)
            # print("====================Extracted content=====================")
            # print(content)
            # print("==========================================================")
            # printStuff(thisFile, callables)
            callablesName = getCallablesName(callables)
            for name, connBlock in callablesName:
                # print(f"Name: {name}, Block name: {connBlock.name}")
                # find name in content
                # name found can be next to any non-word character or start of line and end of line
                regex = re.compile(r'(?<![a-zA-Z0-9_])' + re.escape(name) + r'(?![a-zA-Z0-9_])')
                if regex.search(content):
                    # check if connection already exists
                    if not any(conn.head == block and conn.tail == connBlock and conn.type == ConnectionType.CALL for conn in diagram.connections):
                        diagram.connections.append(Connection(block, connBlock, ConnectionType.CALL))
                        # print(f"Call connection: {block} --> {connBlock}")

def getCallablesName(callables) -> list[tuple]: # type: ignore
    res = []
    for block in callables:
        name = block.name
        type = block.type
        if type in (BlockType.CLASS, BlockType.ABSTRACT_CLASS):
            className = name.split()[0]
            pair = (className, block)
            res.append(pair)
        if type in (BlockType.GLOBAL_VAR, BlockType.CLASS_ATTRIBUTE): 
            # first letter is var type, second letter is var name
            varName = name.split()[1]
            pair = (varName, block)
            res.append(pair)
            pass
        if type in (BlockType.FUNCTION, BlockType.CLASS_FUNCTION):
            # two case: 
            # State<MyHomePage> createState() the function name is createState
            # _addTwoNumbers(int a, int b) the function name is _addTwoNumbers
            match = re.search(r'(\w+)\s*\(.*\)', name)
            if match:
                funcName = match.group(1)
                pair = (funcName, block)
                res.append(pair)
            pass
    return res    

def printStuff(thisFile, callables):
    print("This file:")
    for block in thisFile:
        print(block)
    print("Callables:")
    for block in callables:
        print(block)
    print("=====================================")