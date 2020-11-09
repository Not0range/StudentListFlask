from flask import Flask, url_for, request, jsonify, redirect, make_response
from markupsafe import escape
import requests
import jwt
sql = 'localhost:4200' #'172.18.0.2:4200';
secret = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
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
    res = requests.post('http://' + sql + '/_sql', 
    json={'stmt': 'select * from Students order by id'}).json()
    return jsonify(res['rows'])

@app.route('/last-id', methods=['GET'])
def get_id():
    res = requests.post('http://' + sql + '/_sql', 
    json={'stmt': 'select ID from Students Order by ID desc Limit 1'}).json()
    return str(res['rows'][0][0] + 1) if res['rowcount'] > 0 else '0'

@app.route('/students', methods=['PUT'])
def add_student():
    if requests.post('http://' + sql + '/_sql',
    json={'stmt': 'select * from Cookies Where Cookie = \'' 
    + request.cookies['id'] + '\''}).json()['rowcount'] > 0:
        obj = request.get_json()
        if 'id' in obj and 'fio' in obj and 'course' in obj and 'spec' in obj and 'number' in obj:
            requests.post('http://' + sql + '/_sql',
            json={'stmt': """insert into Students 
            values(%s, '%s', '%s', '%s', '%s')""" % (obj['id'], 
            obj['fio'], obj['course'], obj['spec'], obj['number'])})
            return '',200
        return '', 400
    else:
        return '', 401

@app.route('/students', methods=['POST'])
def edit_student():
    if requests.post('http://' + sql + '/_sql',
    json={'stmt': 'select * from Cookies Where Cookie = \'' 
    + request.cookies['id'] + '\''}).json()['rowcount'] > 0:
        obj = request.get_json()
        if 'id' in obj and 'fio' in obj and 'course' in obj and 'spec' in obj and 'number' in obj:
            requests.post('http://' + sql + '/_sql',
            json={'stmt': """update  Students set fio='%s', course='%s', spec='%s', num='%s' 
            where id=%s""" % (obj['fio'], obj['course'], obj['spec'], obj['number'], obj['id'])})
            return '', 202
        else:
            return '', 400
    else:
        return '', 401

@app.route('/students', methods=['DELETE'])
def delete_student():
    if requests.post('http://' + sql + '/_sql',
    json={'stmt': 'select * from Cookies Where Cookie = \'' 
    + request.cookies['id'] + '\''}).json()['rowcount'] > 0:
        obj = list(map(append_id, request.get_json()))
        res = requests.post('http://' + sql + '/_sql',
        json={'stmt': 'delete from  Students where ' + ' or '.join(obj)}).json()
        return '', 202
    else:
        return '', 401

@app.route('/login', methods=['GET'])
def check_login():
    if 'id' in request.cookies:
        obj = requests.post('http://' + sql + '/_sql',
        json={'stmt': """select Cookies.ID, Cookies.Cookie, Logins.login from Cookies, Logins
         Where Cookies.ID = Logins.ID and Cookie = \'""" 
        + request.cookies['id'] + '\''}).json()
        if obj['rowcount'] > 0:
            return obj['rows'][0][2], 200
        else:
            return '', 401
    else:
            return '', 401

@app.route('/login', methods=['POST'])
def login():
    obj = request.form
    if 'login' in obj and 'password' in obj:
        res = requests.post('http://' + sql + '/_sql',
        json={'stmt': 'select * from Logins Where login = \'' 
        + obj['login'].lower() + '\' and password = \'' + obj['password'] + '\''}).json()
        if res['rowcount'] > 0:
            s = jwt.encode({'login': obj['login']}, secret).decode("utf-8") 
            if requests.post('http://' + sql + '/_sql',
            json={'stmt': 'select * from Cookies Where Cookie = \'' + s + '\''}).json()['rowcount'] == 0:
                requests.post('http://' + sql + '/_sql',
                json={'stmt': 'insert into Cookies Values(%d, \'%s\')' % (res['rows'][0][0], s)})
            resp = make_response(redirect('/'))
            resp.set_cookie('id', s)
            return resp
        else:
            return '', 403
    return '', 400

@app.route('/logout', methods=['GET'])
def logout():
    if 'id' in request.cookies:
        obj = requests.post('http://' + sql + '/_sql',
        json={'stmt': 'select * from Cookies where Cookie = \'' + request.cookies['id'] + '\''}).json()
        if obj['rowcount'] > 0:
            requests.post('http://' + sql + '/_sql',
            json={'stmt': 'delete from Cookies Cookie = \'' + request.cookies['id'] + '\''})
            resp = make_response(redirect('/'))
            resp.set_cookie('id', '')
            return resp
        else:
            return '', 401
    else:
        return '', 401

def append_id(s):
    return 'id = ' + s