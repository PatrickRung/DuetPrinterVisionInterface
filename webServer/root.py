from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/slice', methods=['POST'])
def slice():
    event_data = request.get_json()
    print(event_data)
    return 'Sliced'

if __name__ == '__main__':
    app.run()