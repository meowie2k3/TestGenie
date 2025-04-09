# Project manager module
# This module include git functions, file management functions.

import os
import subprocess


projectDir = os.path.join(os.path.dirname(__file__), 'Projects')
sdkDir = os.path.join(os.path.dirname(__file__), 'SDKs')

class Project:
    
    _framework = ''
    
    def __init__(self, git_url):
        self._git_url = git_url
        self._name = git_url.split('/')[-1]
        # print('Project name: ', self._name)
        if self._name.endswith('.git'):
            self._name = self._name[:-4]
        
        # check if project already cloned
        if os.path.exists(projectDir + '/' + self._name):
            return
        # else:
        #     print(self._clone(git_url))
    
    def _clone(self, git_url):
        # clone the git repository to the project directory
        try:
            # if Project folder not exist, create it
            if not os.path.exists(projectDir):
                os.makedirs(projectDir)
            return subprocess.check_output(['git', 'clone', git_url, projectDir + '/' + self._name], universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Error cloning project: {e}')
    
    def recognizeProjectFramework(self) -> str:
        # TODO: Implement project framework recognition
        return 'flutter'
        pass
    
    def _setFramework(self, framework) -> None:
        self._framework = framework
        
    def getFramework(self) -> str:
        return self._framework
    
    def getName(self) -> str:
        return self._name
    
    def getPath(self) -> str:
        return projectDir + '/' + self._name
    
    def create_test(self, filename, content, isOverWrite = False) -> None:
        # this is abtract method
        # if run in this class, it will raise error
        raise NotImplementedError('This is an abstract method')
    
    def get_test_content(self, filename) -> str:
        # this is abtract method
        # if run in this class, it will raise error
        raise NotImplementedError('This is an abstract method')
    
    def run_test(self, filename) -> tuple:
        # this is abtract method
        # if run in this class, it will raise error
        raise NotImplementedError('This is an abstract method')
    
    def validate(self) -> str:
        # this is abtract method
        # if run in this class, it will raise error
        raise NotImplementedError('This is an abstract method')
    
    def getListSourceFiles(self) -> list:
        # this is abtract method
        # if run in this class, it will raise error
        # logic: sort files by dependency
        raise NotImplementedError('This is an abstract method')
        
    def getFileContent(self, fileDir: str) -> str:
        """_summary_

        Args:
            fileDir (str): file directory relative to project directory

        Returns:
            str: file content
        """
        with open(os.path.join(projectDir, self.getName(), fileDir), 'r') as f:
            return f.read()
    
    @staticmethod
    def getTable():
        from DBMS.Table import Table
        return Table(
            'Project',
            {
                'id': 'INT AUTO_INCREMENT PRIMARY KEY',
                'name': 'VARCHAR(255)',
                'directory': 'VARCHAR(255)',
            }
        )

    
    def __str__(self) -> str:
        return f'Project {self._name} created from {self._git_url}'