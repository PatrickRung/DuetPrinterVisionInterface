from flask import Flask, jsonify, request
import json

# Local module imports
from printBedSlicer.processSVG import sliceToPrintBed
from serializingFunctions import serializeCoordinates
from duet.duetAPI import upload_and_print

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

    # For testing purposes we have this portion upload a test gcode sliced version first!
    # TODO remove when testing is done
    upload_and_print("gcode/Shape-Box_0.25n_0.12mm_PETG_MK3.5_1h4m")

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

    # # Additional parameters that won't be processed by the function and displaced
    # during the API call
    bedXOffsetCM = unpackedDataJson['bedXOffsetCM']
    bedYOffsetCM = unpackedDataJson['bedYOffsetCM']
    print("Received from frontend: " + str(SVGRepresentation))  # "String I need"

    printLocations = sliceToPrintBed(SVGRepresentation, SVGWidthCM, SVGHeightCM, printBedWidthCM, printBedHeightCM)

    printLocAppliedOffset = []

    for coord in printLocations:
        newCoord = [coord[0] + bedXOffsetCM, coord[1] + bedYOffsetCM]
        printLocAppliedOffset.append(newCoord)

    print("locations before offset " + str(printLocations))
    print("locations applied offset " + str(printLocAppliedOffset))

    # Serailize into dictionary
    serializedCoordinates = serializeCoordinates(printLocAppliedOffset)

    # Return satus code 200 that slicing worked
    # Returns a dictionary that contains a list of coordinate distinguished by x and y to be unpacked
    # on the js end
    return jsonify(serializedCoordinates), 200
    

if __name__ == '__main__':
    app.run()