# Project manager module
# This module include git functions, file management functions.

import os
import subprocess

projectDir = os.path.join(os.path.dirname(__file__), 'Projects')

class Project:
    
    _framework = None
    
    def __init__(self, git_url):
        self._git_url = git_url
        self._name = git_url.split('/')[-1]
        # print('Project name: ', self._name)
        if self._name.endswith('.git'):
            self._name = self._name[:-4]
        
        result = self._clone(git_url)
        pass
    
    def _clone(self, git_url):
        # clone the git repository to the project directory
        try:
            subprocess.check_call(['git', 'clone', git_url, projectDir + '/' + self._name])
            return True
        except subprocess.CalledProcessError as e:
            print('Error: ', e)
            return False
    
    def _setFramework(self, framework):
        self._framework = framework
        
    def getFramework(self) -> str:
        return self._framework
    
    def getName(self) -> str:
        return self._name
    
    def __str__(self) -> str:
        return f'Project {self._name} created from {self._git_url}'