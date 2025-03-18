from flask import Flask, request, jsonify
from ProjectManager import Project
from ProjectManager.Flutter import Flutter
from DBMS import DBMS

frameworkMap = {
    'flutter': Flutter
}

app = Flask(__name__)

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
    if not request.json or not 'git_url' in request.json:
        return jsonify({'message': 'Invalid request'})
    git_url = request.json['git_url']
    project = Project(git_url)
    framework = project.recognizeProjectFramework()
    if framework in frameworkMap:
        project = frameworkMap[framework](git_url)
        
    dbms = DBMS(project)
    diagram = dbms.getJsonDiagram()
    return jsonify(diagram)

if __name__ == '__main__':
    app.run()