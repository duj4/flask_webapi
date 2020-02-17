from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_httpauth import HTTPBasicAuth
import config

app = Flask(__name__)
app.config.from_object(config)
auth = HTTPBasicAuth()

tasks = [
    {
        'id': 1,
        'title': 'Buy groceries',
        'description': 'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': 'Learn Python',
        'description': 'Need to find a good Python tutorial on the web',
        'done': False
    }
]

# 添加一个简单的验证
# get_password()是一个回调函数，Flask-HTTPAuth使用它来获取给定的用户名的密码
@auth.get_password
def get_password(username):
    if username == 'jason':
        return 'duj4'
    return None

# 主页
@app.route('/')
def index():
    return "Hello, world!"

# 获取全部task
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    # return jsonify({'tasks':tasks})
    return jsonify({'tasks':list(map(make_public_task, tasks))})

# 根据task_id获取指定task
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task_by_id(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    return jsonify({'task':task[0]})

# 辅助函数，用来生成每个task指定id的URL
def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['url'] = url_for('get_task_by_id', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task

# 插入task
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_tasks():
    if not request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json.get('title', "default title"),
        'description': request.json.get('description', "default description"),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

# 更新task
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)

    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])

    return jsonify({'task': task[0]})

# 删除task
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = list(filter(lambda t:t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': "task %d deleted" % task_id})

# 错误页面
@app.errorhandler(404)
def page_not_found(e):
    print(e.get_description())
    return make_response(jsonify({'error':'Not found'}), 404)

@app.errorhandler(400)
def bad_request(e):
    print(e.get_description())
    return make_response(jsonify({'error':'Bad Request'}), 400)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error':'Unauthorized access'}), 401)

if __name__ == '__main__':
    app.run(debug = app.config['DEBUG'],
            host = app.config['HOST'],
            port = app.config['PORT'])