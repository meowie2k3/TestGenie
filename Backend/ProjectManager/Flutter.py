from ProjectManager import Project, projectDir, os, subprocess, sdkDir

sdkDir = os.path.join(sdkDir, 'flutter')

class Flutter(Project): # Inherit from Project class
    
    def __init__(self, git_url):
        super().__init__(git_url)
        self._setFramework('Flutter')
        self._checkSDK()
        self._flutterPubGet()
        
    def _runFlutterCLI(self, args):
        prjDir = os.path.join(projectDir, self.getName())
        flutterBatDir = os.path.join(sdkDir, 'bin', 'flutter.bat')
        
        cmd = [flutterBatDir]
        # args handling
        if isinstance(args, list):
            cmd.extend(args)
        
        try:
            result = subprocess.check_output(cmd, cwd=prjDir, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error running flutter command: {e}')
        
        return result
    
    def _checkSDK(self):
        # Check if flutter sdk is installed
        if not os.path.exists(sdkDir):
            print('Flutter SDK not found')
            return
        # run sdk from sdkDir
        try:
            result = self._runFlutterCLI('--version')
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error checking flutter sdk: {e}')
        
        # print(result)
    
    def _flutterPubGet(self):
        # prjDir = os.path.join(projectDir, self.getName())
        # flutterBatDir = os.path.join(sdkDir, 'bin', 'flutter.bat')
        
        try:
            # result = subprocess.check_output([flutterBatDir, 'pub', 'get'], cwd=prjDir, universal_newlines=True)
            result = self._runFlutterCLI(['pub', 'get'])
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error running flutter pub get: {e}')
        
        print(result)
        
    def run_test(self):
        pass
    
    
    def __str__(self) -> str:
        return f'Flutter project {self.getName()} created from {self._git_url}'
    
    pass