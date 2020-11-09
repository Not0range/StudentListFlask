from flask import Flask, url_for, request, jsonify
from markupsafe import escape
app = Flask(__name__)
studentList = []

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

@app.route('/<filename>', methods=['GET'])
def src(filename=None):
    return app.send_static_file(filename)

@app.route('/students', methods=['GET'])
def get_list():
    return jsonify(studentList)

@app.route('/last-id', methods=['GET'])
def get_id():
    return str(int(studentList[len(studentList) - 1]["id"]) + 1) if len(studentList) > 0 else '0'

@app.route('/students', methods=['PUT'])
def add_student():
    obj = request.get_json()
    if 'id' in obj and 'fio' in obj and 'course' in obj and 'spec' in obj and 'number' in obj:
        studentList.append(obj)
        return '',201
    return '', 400

@app.route('/students', methods=['POST'])
def edit_student():
    obj = request.get_json()
    if 'id' in obj and 'fio' in obj and 'course' in obj and 'spec' in obj and 'number' in obj:
        i = 0
        while i < len(studentList):
            if studentList[i]['id'] == obj['id']:
                break
            i+=1

        if i < len(studentList):
            studentList[i]['fio'] = obj['fio']
            studentList[i]['course'] = obj['course']
            studentList[i]['spec'] = obj['spec']
            studentList[i]['number'] = obj['number'] 
            return '', 202
        else:
            return '', 400


@app.route('/students', methods=['DELETE'])
def delete_student():
    obj = request.get_json()
    i = 0
    while i < len(studentList):
        if str(studentList[i]['id']) in obj:
            del studentList[i]
            continue
        i+=1
    return '', 202