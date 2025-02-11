from ProjectManager import Project
from ProjectManager.Flutter import Flutter

frameworkMap = {
    'flutter': Flutter
}

def testProject(): # passed
    project = Project('https://github.com/meowie2k3/luckyroll')
    print(project)
    
def testFramework(): # passed
    git_url = 'https://github.com/meowie2k3/sample' # trick my own code lol :v
    project = Project(git_url)
    framework = project.recognizeProjectFramework()
    
    if framework in frameworkMap:
        project = frameworkMap[framework](git_url)
    
    # print(project)
    testError = project.validate()
    if testError != '':
        print("Test error:")
        print(testError)
    else: print("All tests dont have error")
    
def testFiles():
    git_url = 'https://github.com/meowie2k3/sample'
    project = Project(git_url)
    framework = project.recognizeProjectFramework()
    
    if framework in frameworkMap:
        project = frameworkMap[framework](git_url)
        
    sourceFiles = project.getListSourceFiles()
    for file in sourceFiles:
        print(file)
        
    file0Content = project.getFileContent(sourceFiles[0])
    print(file0Content)

if __name__ == '__main__':
    # testProject()
    # testFramework()
    testFiles()
    pass