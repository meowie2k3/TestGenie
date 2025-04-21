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
    
    # print(project.yaml_name)
    testError = project.validate()
    if testError != '':
        print("Test error:")
        print(testError)
    else: print("All tests dont have error")
    
def testFiles(): # passed
    git_url = 'https://github.com/meowie2k3/sample'
    project = Project(git_url)
    framework = project.recognizeProjectFramework()
    
    if framework in frameworkMap:
        project = frameworkMap[framework](git_url)
        
    sourceFiles = project.getListSourceFiles()
    for file in sourceFiles:
        print(file)
    print("==========File content==========")
    file0Content = project.getFileContent(sourceFiles[0])
    print(file0Content)
    print("==========File content==========")
    
def testDiagram():
    from BusinessLogicAnalyzer import DependencyDiagram
    git_url = 'https://github.com/meowie2k3/sample'
    project = Project(git_url)
    framework = project.recognizeProjectFramework()
    
    if framework in frameworkMap:
        project = frameworkMap[framework](git_url)
        
    diagram = DependencyDiagram(project)
    # print(diagram)
    
def test_dbms():
    from DBMS import DBMS
    git_url = 'https://github.com/meowie2k3/sample'
    project = Project(git_url)
    framework = project.recognizeProjectFramework()
    
    if framework in frameworkMap:
        project = frameworkMap[framework](git_url)
        
    dbms = DBMS(project)
    jsonDiagram = dbms.getJsonDiagram()
    print(jsonDiagram)
    # testOriginal = dbms.getBlockOriginalFile(118)
    # print(testOriginal)
    
def test_test_generation():
    from TestGenerator import Test_Generator
    from DBMS import DBMS
    git_url = 'https://github.com/meowie2k3/sample'
    project = Project(git_url)
    framework = project.recognizeProjectFramework()
    
    if framework in frameworkMap:
        project = frameworkMap[framework](git_url)
        
    dbms = DBMS(project)
    
    tg = Test_Generator()
    
    testing_block_id = 183
    
    testFileContent = tg.generate_test_case(
        package_name= project.getName(),
        code_location=dbms.getBlockOriginalFile(testing_block_id),
        function_name_and_arguments=dbms.getBlockName(testing_block_id),
        prediction=dbms.getBlockPrediction(testing_block_id),
    )
    # print(testFileContent)
    test_filename = 'first_test.dart'
    project.create_test(
        filename=test_filename,
        content=testFileContent,
        isOverWrite=True
    )
    # validation process
    run_result, run_error = project.run_test(test_filename)
    iteration_limit = 10
    while run_error != '' and iteration_limit > 0:
        new_test_content = tg.fix_generated_code(
            error_message=run_error,
            current_test_code=project.get_test_content(test_filename),
            prediction=dbms.getBlockPrediction(testing_block_id),
        )
        # print(new_test_content)
        project.create_test(
            filename=test_filename,
            content=new_test_content,
            isOverWrite=True
        )
        run_result, run_error = project.run_test(test_filename)
        print(run_error)
        # safe guard, avoid infinite loop
        iteration_limit -= 1
    
def test_run_test():
    git_url = 'https://github.com/meowie2k3/sample'
    project = Project(git_url)
    framework = project.recognizeProjectFramework()
    
    if framework in frameworkMap:
        project = frameworkMap[framework](git_url)
        
    run_result, run_error = project.run_test('block_183_test.dart')
    # print(run_result)
    print("==========Test result==========")
    print(run_result)
    print("==========Test error==========")
    print(run_error)
    # print(run_error == '')
    # fileContent = project.get_test_content('first_test.dart')
    # print(fileContent)

if __name__ == '__main__':
    # testProject()
    # testFramework()
    # testFiles()
    # testDiagram()
    # test_dbms()
    # test_test_generation()
    test_run_test()
    pass