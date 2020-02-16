from flask import Flask
import config

app = Flask(__name__)
app.config.from_object(config)

@app.route('/')
def index():
    return "Hello, world!"

if __name__ == '__main__':
    app.run(debug = app.config['DEBUG'],
            host = app.config['HOST'],
            port = app.config['PORT'])