from ..Diagram.Block import Block, BlockType
from ..Diagram.Connection import Connection, ConnectionType
import os
import re

def CallAnalyzer(diagram, block, visited = []):
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
    callable.extend(thisFile)
    
    call_pattern = re.compile(r'(\w+)\s*\(')
    
    for block in thisFile:
        if block in visited:
            continue
        # ignore file, class, enum
        if block.type in (BlockType.AbstractClass, BlockType.CLASS, BlockType.ENUM):
            innerBlocks = [conn.tail for conn in diagram.connections if conn.head == block and conn.type == ConnectionType.CONTAIN]
            # magic recursive calls at 4 a.m
            _CallAnalyzer(diagram, innerBlocks, callables, visited)
            
            visited.append(block)
            continue
        else:
            visited.append(block)
            # analyze calls in block
            # If called, create a connection ConnectionType.CALL
            content = block.getContentNoComment()
            # content will contain  name itself
            # or 
            calls = call_pattern.findall(content)
    pass