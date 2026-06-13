from flask import Flask, jsonify, request
import json
from flask_cors import CORS

# Local module imports
from printBedSlicer.processSVG import sliceToPrintBed
from serializingFunctions import serializeCoordinates
from printBedSlicer.duet.duetAPI import upload_and_print, home_printer

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/', methods=['GET'])
def home():
    return jsonify({'data': 'hello world'})

@app.route('/homeprinter', methods=['POST'])
def homeprinter():
    home_printer()
    return jsonify({}), 200

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

@app.route('/execLocalizedPrint', methods=['POST'])
def execLocalizedPrint():
    """
    Function for performing print at location however, it first uses the CV to perform localization
    on itself again. Then it applies the offset when sending svg to slicer.
    
    The name `chunk_name` 
    This function expects the size of the aruco markers within the request as
    well as the aruco marker ids
    """
    body = request.get_json()          # Parse the JSON body

    if not body or 'data' not in body:
        return jsonify({"error": "Missing 'data' in JSON body"}), 400
    
    unpackedData = body['data']
    unpackedDataJson = json.loads(unpackedData)

    fileName = unpackedDataJson['chunk_name']                # Unpack the string
    marker_length = unpackedDataJson['marker_length']                # Unpack the string
    ID1 = unpackedDataJson['ID1']                # Unpack the string
    ID2 = unpackedDataJson['ID2']                # Unpack the string
    
    localize_slice_print(str(fileName))
    return jsonify(), 200

if __name__ == '__main__':
    # Listen on all interfaces. Just have to type in IP followed by port
    app.run(host='0.0.0.0', port=5000)
    CORS(app)