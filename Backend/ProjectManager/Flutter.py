from ProjectManager import Project, projectDir, os, subprocess, sdkDir

sdkDir = os.path.join(sdkDir, 'flutter')

class Flutter(Project): # Inherit from Project class
    
    def __init__(self, git_url):
        super().__init__(git_url)
        self._setFramework('Flutter')
        self._checkSDK()
        self._flutterPubGet()
    
    def _checkSDK(self):
        # Check if flutter sdk is installed
        if not os.path.exists(sdkDir):
            print('Flutter SDK not found')
            return
        # run sdk from sdkDir
        try:
            result = subprocess.check_output([os.path.join(sdkDir, 'bin', 'flutter.bat'), '--version'], universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error checking flutter sdk: {e}')
        
        # print(result)
        pass
    
    def _flutterPubGet(self):
        # run flutter pub get for the project
        prjDir = os.path.join(projectDir, self.getName())
        flutterBatDir = os.path.join(sdkDir, 'bin', 'flutter.bat')
        
        try:
            result = subprocess.check_output([flutterBatDir, 'pub', 'get'], cwd=prjDir, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error running flutter pub get: {e}')
        
        print(result)
    
    def __str__(self) -> str:
        return f'Flutter project {self.getName()} created from {self._git_url}'
    
    pass