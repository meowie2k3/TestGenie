from ProjectManager import Project, projectDir, os, subprocess, sdkDir

sdkDir = os.path.join(sdkDir, 'flutter')

class Flutter(Project): # Inherit from Project class
    
    def __init__(self, git_url):
        super().__init__(git_url)
        self._setFramework('Flutter')
        self._checkSDK()
        self._flutterPubGet()
        self._addTestDependency()
        self.yaml_name = self._getYamlName()
        # self._createSampleProject('sample')
        
    def _runFlutterCLI(self, args, isRaiseException=False) -> tuple:
        prjDir = os.path.join(projectDir, self.getName())
        flutterBatDir = os.path.join(sdkDir, 'bin', 'flutter')

        cmd = [flutterBatDir]
        # args handling
        # if args is a string that have space, convert it to list
        if isinstance(args, str) and ' ' in args:
            args = args.split()
        if isinstance(args, list):
            cmd.extend(args)
            
        # run cmd via subprocess
        try:
            process = subprocess.Popen(cmd, cwd=prjDir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, encoding='utf-8', shell=True)
            stdout, stderr = process.communicate()
            if process.returncode != 0 and isRaiseException:
                raise Exception(f'Error running flutter command: {stderr}')
            return stdout, stderr
        except subprocess.CalledProcessError as e:
            if isRaiseException:
                raise Exception(f'Error running flutter command: {e}')
            return e.__dict__, e.args
    
    def _checkSDK(self) -> None:
        # Check if flutter sdk is installed
        if not os.path.exists(sdkDir):
            print('Flutter SDK not found')
            return
        # run sdk from sdkDir
        try:
            self._runFlutterCLI('--version', isRaiseException=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error checking flutter sdk: {e}')
        
        # print(result)
    
    def _getYamlName(self) -> str:

        yamlContent = self.getFileContent('pubspec.yaml')
        # print(yamlContent)
        # first line should define the name of the project: "name: ....."
        return yamlContent.split('\n')[0].split('name: ')[1].strip()

    
    # function for testing only. Do not use in production
    def _createSampleProject(self, prjName) -> str:
        try:
            # cannot use _runFlutterCLI because no project directory yet
            # result = self._runFlutterCLI(['create', prjName], isRaiseException=True)
            result = subprocess.check_output([os.path.join(sdkDir, 'bin', 'flutter'), 'create', prjName],cwd=projectDir, universal_newlines=True, encoding='utf-8',  shell=True)
            
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error creating flutter project: {e}')
        return result
    
    def _flutterPubGet(self) -> None:
        # prjDir = os.path.join(projectDir, self.getName())
        # flutterBatDir = os.path.join(sdkDir, 'bin', 'flutter.bat')
        
        try:
            # result = subprocess.check_output([flutterBatDir, 'pub', 'get'], cwd=prjDir, universal_newlines=True)
            self._runFlutterCLI(['pub', 'get', '--no-example'], isRaiseException=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error running flutter pub get: {e}')
        
        # print(result)
        
    def _addTestDependency(self) -> None:
        # run pub add test
        try:
            self._runFlutterCLI(['pub', 'add', 'test'], isRaiseException=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error adding test dependency: {e}')
        # print(result)
    
    def create_test(self, filename, content, isOverWrite = False) -> None:
        # create test file in the test directory
        # check if test directory exists
        testDir = os.path.join(projectDir, self.getName(), 'test')
        if not os.path.exists(testDir):
            os.makedirs(testDir)
        # check if file exists
        fileDir = os.path.join(testDir, filename)
        if os.path.exists(fileDir) and not isOverWrite:
            raise Exception(f'File {fileDir} already exists')
        # create file
        with open(fileDir, 'w') as f:
            f.write(content)
            
    def get_test_content(self, filename) -> str:
        # use getFileContent to get the content of the test file
        testDir = os.path.join(projectDir, self.getName(), 'test')
        fileDir = os.path.join(testDir, filename)
        if not os.path.exists(fileDir):
            raise Exception(f'File {fileDir} does not exist')
        return self.getFileContent(fileDir)
    
    # return tuple (result, error)
    def run_test(self, filename) -> tuple:
        fileDir = os.path.join('test', filename)
        try:
            result = self._runFlutterCLI(['test', fileDir])
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error running flutter test: {e}')
        return result
        pass
    
    def validate(self) -> str:
        # run all tests in the test directory
        testDir = os.path.join(projectDir, self.getName(), 'test')
        for file in os.listdir(testDir):
            if file.endswith('.dart'):
                result, err = self.run_test(file)
                if err:
                    return err
                
        return ''
    
    def getListSourceFiles(self) -> list[str]:
            """_summary_

            Returns:
                list[str]: list of source files in the project relative to project directory
            """
            prjDir = os.path.join(projectDir, self.getName())
            libDir = os.path.join(prjDir, 'lib') 
            sourceFiles = []
            
            # find main.dart first
            if os.path.exists(os.path.join(libDir, 'main.dart')):
                sourceFiles.append(os.path.relpath(os.path.join(libDir, 'main.dart'), prjDir))
            
            for root, dirs, files in os.walk(libDir):
                for file in files:
                    if file.endswith('.dart') and os.path.relpath(os.path.join(root, file), prjDir) not in sourceFiles:
                        sourceFiles.append(os.path.relpath(os.path.join(root, file), prjDir))
                        
            return sourceFiles
    
    def __str__(self) -> str:
        return f'Flutter project {self.getName()} created from {self._git_url}'
    
    pass