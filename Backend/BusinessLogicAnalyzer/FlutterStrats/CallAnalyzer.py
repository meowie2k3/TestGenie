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
            
            connectedBlocks.extend(currentBlocks)
        
            _CallAnalyzer(diagram, currentBlocks, connectedBlocks, visited)
        
def _CallAnalyzer(diagram, thisFile, callables, visited=[]):
    # thisFile: blocks of contains in current file
    # callables: blocks of contains in imported file
    
    call_pattern = re.compile(r'(\w+)\s*\(')
    
    for block in thisFile:
        if block in visited:
            continue
        # ignore file, class, enum
        if block.type in (BlockType.FILE, BlockType.CLASS, BlockType.ENUM):
            continue
        visited.append(block)
        # analyze calls in block
        # If called, create a connection ConnectionType.CALL
        content = block.getContentNoComment()
        # content will contain  name itself
        # or 
        calls = call_pattern.findall(content)
        
        print(calls)
        for block2 in callables:
            print(block2)
    pass