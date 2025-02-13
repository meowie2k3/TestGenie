from ..Diagram.Block import Block
from ..Diagram.Connection import Connection, ConnectionType
import os

def FileToClassAnalyzer(diagram, block):
    currContent = block.content
    currType = block.type
    
    print("Current content: ", currContent)
    print("Current type: ", currType)