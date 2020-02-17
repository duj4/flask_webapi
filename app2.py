from flask import Flask, abort, jsonify, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
import config

app = Flask(__name__)
app.config.from_object(config)
api = Api(app)
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

task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}

@auth.get_password
def get_password(username):
    if username == 'jason':
        return 'duj4'
    return None

class TaskListAPI(Resource):
    decorators = [auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True, help='No task title provided', location='json')
        self.reqparse.add_argument('description', type=str, default="", location='json')
        self.reqparse.add_argument('done', type=bool, default=False, location='json')
        super(TaskListAPI, self).__init__()

    # 获取所有task
    def get(self):
        return {'tasks':marshal(tasks, task_fields)}

    # 插入新task
    def post(self):
        task = {}
        task['id'] = tasks[-1]['id'] + 1
        args = self.reqparse.parse_args()
        for k, v in args.items():
            task[k] = v
        tasks.append(task)
        return {'task': marshal(task, task_fields)}, 201

class TaskAPI(Resource):
    decorators = [auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    # 获取某个task
    def get(self, id):
        task = list(filter(lambda t: t['id'] == id, tasks))
        if len(task) == 0:
            abort(404)
        return {'task':marshal(task, task_fields)}

    # 更新某个task
    def put(self, id):
        task = list(filter(lambda t: t['id'] == id, tasks))
        if len(task) == 0:
            abort(404)
        task = task[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v != None:
                task[k] = v
        return {'task':marshal(task, task_fields)}

    # 删除某个task
    def delete(self, id):
        task = list(filter(lambda t: t['id'] == id, tasks))
        if len(task) == 0:
            abort(404)
        tasks.remove(task[0])
        return {'result': "task %d deleted" % id}

api.add_resource(TaskListAPI, '/todo/api/v1.0/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<int:id>', endpoint='task')

@app.route('/')
def index():
    return "Hello, world!"

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