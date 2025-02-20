from ..Diagram.Block import Block, BlockType
from ..Diagram.Connection import Connection, ConnectionType
import os
import re

def ClassExtensionAnalyze(diagram):
    # find class and abstract class is a subclass of another class
    
    classBlock = [block for block in diagram.blocks if block.type == BlockType.CLASS]
        
    for block in classBlock:
        print(block)