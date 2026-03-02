from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/', methods=['GET'])
def home():
    return jsonify({'data': 'hello world'})

@app.route('/slice', methods=['PUT'])
def events():
    event_data = request.json
    print(event_data)

if __name__ == '__main__':
    app.run()