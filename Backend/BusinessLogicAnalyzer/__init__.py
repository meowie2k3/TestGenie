from ProjectManager import Project
from .Flutter import FlutterAnalyzeStrategy
from .AI_Agent import AI_Agent

class DependencyDiagram:
    
    blocks = []
    connections = []
    
    def __init__(self, project: Project) -> None:
        self.project = project
        self._generateDiagram()
        self.ai_agent = AI_Agent()
        self._getPredictions()
    
    def _generateDiagram(self) -> None:
        # Analyze project abstractly to project's framework
        framework = self.project.getFramework()
        functionName = framework + 'AnalyzeStrategy'
        if functionName in globals():
            globals()[functionName](self)
        else:
            raise Exception('Framework not supported')
        
    def _getPredictions(self) -> None:
        for block in self.blocks:
            block.setPrediction(self.ai_agent.generate_BLA_prediction(source_code=block.getContentNoComment(), chat_history=[]))
        
    def __str__(self) -> str:
        """_summary_

        Returns:
            str: project name, list of blocks and connections in the diagram
        """
        res = f'Project: {self.project.getName()}\n'
        res += 'Blocks:\n'
        for block in self.blocks:
            res += f'{block.name} - {block.type}\n'
        res += 'Connections:\n'
        for connection in self.connections:
            res += f'{connection.head.name} -> {connection.tail.name} - {connection.type}\n'
        return res
        