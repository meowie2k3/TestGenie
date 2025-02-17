from ..Diagram.Block import Block, BlockType
from ..Diagram.Connection import Connection, ConnectionType
import os

def CallAnalyzer(diagram, block, visited = []):
    visited.append(block)
    
    currType = block.type
    
    # strat: 2-layer recursive
    if currType == BlockType.FILE:
        # find connected file (imported file)
        connectedFiles = [conn.tail for conn in diagram.connections if conn.head == block and conn.type == ConnectionType.IMPORT]
        
        for file in connectedFiles:
            print(file)