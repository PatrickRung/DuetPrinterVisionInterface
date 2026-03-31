from flask import Flask, jsonify, request
import json

# Local module imports
from printBedSlicer.processSVG import sliceToPrintBed

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/', methods=['GET'])
def home():
    return jsonify({'data': 'hello world'})

@app.route('/home/<int:num>', methods=['GET'])
def disp(num):
    return jsonify({'data': num ** 2})

# API call for slicing the SVG and returning the coordinates to the user
@app.route('/slice', methods=['POST'])
def Slice():
    body = request.get_json()          # Parse the JSON body

    if not body or 'data' not in body:
        return jsonify({"error": "Missing 'data' in JSON body"}), 400
    
    unpackedData = body['data']
    unpackedDataJson = json.loads(unpackedData)

    SVGRepresentation = unpackedDataJson['SVGData']                # Unpack the string
    SVGWidthCM = unpackedDataJson['SVGWidthCM']
    SVGHeightCM = unpackedDataJson['SVGHeightCM']
    printBedWidthCM = unpackedDataJson['printBedWidthCM']
    printBedHeight = unpackedDataJson['printBedHeightCM']

    # # Additional parameters that won't be processed by the function and displaced
    # during the API call
    bedXOffsetCM = unpackedDataJson['bedXOffsetCM']
    bedYOffsetCM = unpackedDataJson['bedYOffsetCM']
    print("Received from frontend: " + str(SVGRepresentation))  # "String I need"

    res = sliceToPrintBed(SVGRepresentation, SVGWidthCM, SVGHeightCM, printBedWidthCM, printBedHeight)

    # Return satus code 200 that slicing worked
    return jsonify({"received": ""}), 200
    

if __name__ == '__main__':
    app.run()