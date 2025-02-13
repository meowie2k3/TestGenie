from ..Diagram.Block import Block
from ..Diagram.Connection import Connection, ConnectionType
import os

def ContainAnalyzer(diagram, block):
    currType = block.type
    
    # print("Current content: ", currContent)
    # print("Current type: ", currType)
    
    # keep analyze unless the block is a function
    if (currType != 'Function'):
        content = block.getContentNoComment()
        print(content)
        pass