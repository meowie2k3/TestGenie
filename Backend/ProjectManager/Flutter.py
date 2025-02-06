from ProjectManager import Project, projectDir, os, subprocess, sdkDir

sdkDir = sdkDir + '/flutter'

class Flutter(Project): # Inherit from Project class
    
    def __init__(self, git_url):
        super().__init__(git_url)
        self._setFramework('Flutter')
        self._checkSDK()
        pass
    
    def _checkSDK(self):
        # Check if flutter sdk is installed
        print(sdkDir)
        pass
    
    def __str__(self) -> str:
        return f'Flutter project {self.getName()} created from {self._git_url}'
    
    pass