from flask import Flask, jsonify, request
import json
from flask_cors import CORS

# Local module imports
from printBedSlicer.processSVG import sliceToPrintBed
from serializingFunctions import serializeCoordinates
from duet.duetAPI import upload_and_print, get_print_status

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/', methods=['GET'])
def home():
    return jsonify({'data': 'hello world'})

@app.route('/printstate', methods=['GET'])
def disp():
    return jsonify({'data': get_print_status()})

# API call for slicing the SVG and returning the coordinates to the user
@app.route('/slice', methods=['POST'])
def slice():

    body = request.get_json()          # Parse the JSON body

    if not body or 'data' not in body:
        return jsonify({"error": "Missing 'data' in JSON body"}), 400
    
    unpackedData = body['data']
    unpackedDataJson = json.loads(unpackedData)

    SVGRepresentation = unpackedDataJson['SVGData']                # Unpack the string
    SVGWidthCM = unpackedDataJson['SVGWidthCM']
    SVGHeightCM = unpackedDataJson['SVGHeightCM']
    printBedWidthCM = unpackedDataJson['printBedWidthCM']
    printBedHeightCM = unpackedDataJson['printBedHeightCM']

    # Additional parameters that won't be processed by the function and displaced
    # during the API call
    bedXOffsetCM = unpackedDataJson['bedXOffsetCM']
    bedYOffsetCM = unpackedDataJson['bedYOffsetCM']
    print("Received from frontend: " + str(SVGRepresentation))

    # Returns list of [x, y, rotation] triples
    printLocations = sliceToPrintBed(SVGRepresentation, SVGWidthCM, SVGHeightCM, printBedWidthCM, printBedHeightCM)

    # Apply bed offset to x and y, preserve rotation as-is
    printLocAppliedOffset = [
        [coord[0] + bedXOffsetCM, coord[1] + bedYOffsetCM, coord[2]]
        for coord in printLocations
    ]

    print("locations before offset " + str(printLocations))
    print("locations applied offset " + str(printLocAppliedOffset))

    # Serialize into dictionary
    serializedCoordinates = serializeCoordinates(printLocAppliedOffset)

    # Return status code 200 that slicing worked
    # Returns a dictionary that contains a list of coordinates distinguished by x, y, and
    # rotation to be unpacked on the js end
    return jsonify(serializedCoordinates), 200

@app.route('/execPrint', methods=['POST'])
def execPrint():
    body = request.get_json()          # Parse the JSON body

    if not body or 'data' not in body:
        return jsonify({"error": "Missing 'data' in JSON body"}), 400
    
    unpackedData = body['data']
    unpackedDataJson = json.loads(unpackedData)

    fileName = unpackedDataJson['fname']                # Unpack the string
    
    upload_and_print(str(fileName))
    return jsonify(), 200

if __name__ == '__main__':
    # Listen on all interfaces. Just have to type in IP followed by port
    app.run(host='0.0.0.0', port=5000)
    CORS(app)