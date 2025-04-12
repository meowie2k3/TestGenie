from flask import Flask, request, jsonify
from flask_cors import CORS
from ProjectManager import Project
from ProjectManager.Flutter import Flutter
from DBMS import DBMS
from TestGenerator import Test_Generator

frameworkMap = {
    'flutter': Flutter
}

def getDBMS(git_url) -> DBMS:
    project = Project(git_url)
    framework = project.recognizeProjectFramework()
    
    if framework in frameworkMap:
        project = frameworkMap[framework](git_url)
        
    dbms = DBMS(project)
    
    return dbms

app = Flask(__name__)
CORS(app)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, World!'})

@app.route('/hello/<name>', methods=['GET'])
def hello_name(name):
    return jsonify({'message': f'Hello, {name}!'})

# Post git project url
@app.route('/createProject', methods=['POST'])
def createProject():
    if not request.json or not 'git_url' in request.json:
        return jsonify({'message': 'Invalid request'})
    git_url = request.json['git_url']
    project = Project(git_url)
    # print(project)
    return jsonify({'message': f'{project}'})

@app.route('/getDiagram', methods=['POST'])
def getDiagram():
    # print(request.json)
    if not request.json or not 'git_url' in request.json:
        return jsonify({'message': 'Invalid request'})
    git_url = request.json['git_url']
    
    dbms = getDBMS(git_url)
    
    diagram = dbms.getJsonDiagram()
    return jsonify(diagram)

@app.route('/getDiagram', methods=['OPTIONS'])
def getDiagramOptions():
    print(request.json)
    print("wrong method")
    return jsonify({'message': 'Options request'})

@app.route('/getBlockContent', methods=['POST'])
def getBlockContent():
    if not request.json or not 'git_url' in request.json or not 'block_id' in request.json:
        return jsonify({'message': 'Invalid request'})
    git_url = request.json['git_url']
    blockId = request.json['block_id']
    
    dbms = getDBMS(git_url)
    blockContent = dbms.getBlockContent(blockId)
    return jsonify(blockContent)
    
@app.route('/getBlockPrediction', methods=['POST'])
def getBlockPrediction():
    if not request.json or not 'git_url' in request.json or not 'block_id' in request.json:
        return jsonify({'message': 'Invalid request'})
    git_url = request.json['git_url']
    blockId = request.json['block_id']
    
    dbms = getDBMS(git_url)
    blockPrediction = dbms.getBlockPrediction(blockId)
    return jsonify(blockPrediction)

@app.route('/getBlockDetail', methods=['POST'])
def getBlockDetail():
    if not request.json or not 'git_url' in request.json or not 'block_id' in request.json:
        return jsonify({'message': 'Invalid request'})
    git_url = request.json['git_url']
    blockId = request.json['block_id']
    
    dbms = getDBMS(git_url)
    # {
       # 'content': blockContent,
         # 'prediction': blockPrediction, 
    # }
    content = dbms.getBlockContent(blockId)
    prediction = dbms.getBlockPrediction(blockId)
    try: 
        test_file_content = dbms.project.get_test_content ('block_' + str(blockId) + '_test.dart')
    except Exception as e:
        test_file_content = ''
        
    return jsonify({
        'content': content,
        'prediction': prediction,
        'test_file_content': test_file_content,
    })

# dont know why this is needed
@app.route('/getBlockDetail', methods=['OPTIONS'])
def getBlockDetailOptions():
    print(request.json)
    print("wrong method")
    return jsonify({'message': 'Options request'})

@app.route('/updateBlockPrediction', methods=['POST'])
def updateBlockPrediction():
    if not request.json or not 'git_url' in request.json or not 'block_id' in request.json or not 'prediction' in request.json:
        return jsonify({'message': 'Invalid request'})
    git_url = request.json['git_url']
    blockId = request.json['block_id']
    prediction = request.json['prediction']
    
    dbms = getDBMS(git_url)
    dbms.updateBlockPrediction(blockId, prediction)
    
    return jsonify(
        {
            'message': 'Update success!',
            'code': 200,
            'success': True,
        }
    )

@app.route('/updateBlockPrediction', methods=['OPTIONS'])
def updateBlockPredictionOptions():
    print(request.json)
    print("wrong method")
    return jsonify({'message': 'Options request'})
    
@app.route('/generateTest', methods=['POST'])
def generateTest():
    try:
        if not request.json or not 'git_url' in request.json or not 'block_id' in request.json:
            return jsonify({'message': 'Invalid request'})
        git_url = request.json['git_url']
        blockId = request.json['block_id']
        
        dbms = getDBMS(git_url)
        tg = Test_Generator()
        
        testFileContent = tg.generate_test_case(
            package_name= dbms.project.getName(),
            code_location=dbms.getBlockOriginalFile(blockId),
            function_name_and_arguments=dbms.getBlockName(blockId),
            prediction=dbms.getBlockPrediction(blockId),
        )
        file_name = 'block_' + str(blockId) + '_test.dart'
        
        dbms.project.create_test(
            filename=file_name,
            content=testFileContent,
            isOverWrite=True
        )
        # validation process
        run_result, run_error = dbms.project.run_test(file_name)
        iteration_limit = 5
        while run_error != '' and iteration_limit > 0:
            new_test_content = tg.fix_generated_code(
                error_message=run_error,
                code_location=dbms.getBlockOriginalFile(blockId),
                function_name_and_arguments=dbms.getBlockName(blockId),
                prediction=dbms.getBlockPrediction(blockId),
            )
            dbms.project.create_test(
                filename=file_name,
                content=new_test_content,
                isOverWrite=True
            )
            run_result, run_error = dbms.project.run_test(file_name)
            iteration_limit -= 1
        
        return jsonify(
            {
                'message': 'Test generation success!',
                'code': 200,
                'success': True,
                'test_file_content': testFileContent,
            }
        )
    except Exception as e:
        return jsonify({'message': str(e)})

@app.route('/generateTest', methods=['OPTIONS'])
def generateTestOptions():
    print(request.json)
    print("wrong method")
    return jsonify({'message': 'Options request'})
    
if __name__ == '__main__':
    app.run(debug=True)