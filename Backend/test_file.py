from ProjectManager import Project
from ProjectManager.Flutter import Flutter

frameworkMap = {
    'flutter': Flutter
}

def testProject():
    project = Project('https://github.com/meowie2k3/luckyroll')
    print(project)
    
def testFramework():
    git_url = 'https://github.com/meowie2k3/sample' # trick my own code lol :v
    project = Project(git_url)
    framework = project.recognizeProjectFramework()
    
    if framework in frameworkMap:
        project = frameworkMap[framework](git_url)
    
    # print(project)
    testResult, testError = project.run_test('widget_test.dart')
    
    print("Test result:" )
    print(testResult)
    print("Test error:")
    print(testError)
    
    pass

if __name__ == '__main__':
    testFramework()