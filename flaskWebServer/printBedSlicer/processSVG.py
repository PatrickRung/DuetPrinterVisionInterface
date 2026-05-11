from svg.path import parse_path
from svg.path.path import Line
from svg.path.path import QuadraticBezier
from svg.path.path import CubicBezier
from xml.dom import minidom
from xml.dom.minidom import parse, parseString, Document

import matplotlib.pyplot as plt
import numpy as np
import os

# Local imports (Use a . in front for relative dir imports)
from .rendering.chunkRepresentation import chunkRepresentation
from .gcodeslice import slice_svg

def compPoint(p1, p2):
    status = p1[0] == p2[0] and p1[1] == p2[1]
    print(status)
    return status

def pointDist(p1, p2):
    return np.sqrt(np.square(p1[0] - p2[0]) + np.square(p1[1] - p2[1]))

def chunkRotation(chunkStartPoint, chunkEndPoint):
    """
    Compute the angle perpendicular to the chunk's travel direction.
    Convention: up (negative Y) = 0 degrees, east (positive X) = 90 degrees.
    The perpendicular is the chunk direction rotated 90 degrees clockwise.
    """
    dx = chunkEndPoint[0] - chunkStartPoint[0]
    dy = chunkEndPoint[1] - chunkStartPoint[1]

    # Angle of the chunk's travel direction using atan2.
    # SVG Y-axis is flipped (down = positive), so negate dy for standard math convention.
    # atan2 with (x, -y) gives angle from "up" axis, clockwise positive.
    travel_angle_deg = np.degrees(np.arctan2(dx, -dy)) % 360

    # Perpendicular = rotate travel direction 90 degrees clockwise
    perp_angle_deg = (travel_angle_deg + 90) % 360

    return perp_angle_deg

# The SVG will fit the entire size of the bed size.
def sliceToPrintBed(SVGFileInput: str, 
                    SVGWidthCM: int,
                    SVGHeightCM: int,
                    printBedWidthCM: int, 
                    printBedHeightCM: int):
    
    # Data to return — each element is [x, y, rotation_degrees]
    printLocations = []

    # read the SVG file
    domSVG = parseString(SVGFileInput)
    svgRef = domSVG.getElementsByTagName('svg')

    pixelWidth = svgRef[0].getAttribute('width')
    pixelHeight = svgRef[0].getAttribute('height')
    
    path_strings = [path.getAttribute('d') for path
                    in domSVG.getElementsByTagName('path')]
    
    # Get raw XML for easy manipulation of XML representation as well as easy transfering back
    # to XML at the end
    path_raw_xml = [path for path
                    in domSVG.getElementsByTagName('path')]
    
    # If these are different length we went wrong somewhere
    assert len(path_strings) == len(path_raw_xml)

    # Multiply any pixel value against these values to get the CM width
    pixelToCMWidth = SVGWidthCM / float(pixelWidth)
    pixelToCmHeight = SVGHeightCM / float(pixelHeight)

    printBedWidthPixels = printBedWidthCM / pixelToCMWidth

    fig, ax = plt.subplots()
    fig.set_figheight(10)
    fig.set_figwidth(10)

    currPoint = [-1, -1]
    chunkRepList = []

    # Each chunk has it's own dedicated XML document that will be converted to XML later down the line
    currChunk = chunkRepresentation(printBedWidthCM, printBedHeightCM)

    # Track the start point of the current chunk for rotation calculation
    currChunkStartPoint = None
    
    # Draw the shape out on MatPlotLib
    iterator = 0
    printBedDistRemaining = printBedWidthPixels
    for path_string in path_strings:
        path = parse_path(path_string)
        # Assume that there is only one element per path
        # Move to end of print bed

        for currElement in path:
            if isinstance(currElement, Line):
                
                # Get data
                x0 = currElement.start.real
                y0 = currElement.start.imag
                x1 = currElement.end.real
                y1 = currElement.end.imag

                startPoint = np.array([x0, y0])
                endPoint = np.array([x1, y1])

                # Display on screen
                ax.plot(x0, y0, marker='o')
                ax.plot(x1, y1, marker='o')
                ax.plot(np.array([x0, x1]), np.array([y0, y1]), 'ro-', color='green')
                print("(%.2f, %.2f) - (%.2f, %.2f)" % (x0, y0, x1, y1))

                # If first point
                if compPoint(currPoint, [-1, -1]):
                    currPoint = np.array([x0, y0])

                # Track the start of the current chunk on its first line segment
                if currChunkStartPoint is None:
                    currChunkStartPoint = np.array([x0, y0])

                currPointEndLineDist = pointDist(currPoint, np.array([x1, y1]))

                while True:
                    currPointEndLineDist = pointDist(currPoint, endPoint)
                    if currPointEndLineDist <= 0:
                        break
                    if currPointEndLineDist - printBedDistRemaining < 0:
                        currChunk.appendLine(currPoint[0], currPoint[1], x1, y1)
                        printBedDistRemaining -= currPointEndLineDist
                        print("Dist between points " + str(currPointEndLineDist))
                        currPoint = np.array([x1, y1])
                        break

                    # Store current point for reference later
                    cachedCurrPoint = currPoint

                    # Get bisection point where the chunk ends
                    unit = (endPoint - startPoint) / pointDist(startPoint, endPoint)
                    bisect_point = currPoint + (unit * printBedDistRemaining)
                    ax.plot(bisect_point[0], bisect_point[1], marker='o', color = 'blue')
                    currPoint = bisect_point

                    # Update path tracing state
                    printBedDistRemaining = printBedWidthPixels

                    # Handle SVG
                    currChunk.appendLine(cachedCurrPoint[0], 
                                            cachedCurrPoint[1],
                                            bisect_point[0], 
                                            bisect_point[1])

                    # Compute rotation: perpendicular to the chunk's start->end direction
                    chunkEndPoint = bisect_point
                    rotation = chunkRotation(currChunkStartPoint, chunkEndPoint)

                    # Reset chunk start for next chunk
                    currChunkStartPoint = bisect_point

                    # Reset chunk data and account for chunk
                    chunkRepList.append(currChunk)
                    currChunkPrintLoc = currChunk.getPrintLocation()
                    

                    # Denote on matplot lib in red where the Roborock will park
                    ax.plot(currChunkPrintLoc[0], currChunkPrintLoc[1], marker='o', color='red')

                    # Modify to be prop
                    currChunkPrintLoc[0] = currChunkPrintLoc[0] * pixelToCMWidth
                    currChunkPrintLoc[1] = currChunkPrintLoc[1] * pixelToCmHeight
                    printLocations.append([currChunkPrintLoc[0], currChunkPrintLoc[1], rotation])

                    currChunk.reorientInPrintSpace(pixelToCMWidth, pixelToCmHeight)
                    if __name__ == '__main__':
                        currChunk.displayChunk()
                    currChunk = chunkRepresentation(printBedWidthCM, printBedHeightCM)

        iterator += 1

    # Final chunk
    currChunkPrintLoc = currChunk.getPrintLocation()

    # Denote on matplot lib in red where the Roborock will park
    ax.plot(currChunkPrintLoc[0], currChunkPrintLoc[1], marker='o', color='red')

    # Compute rotation for the final chunk
    # currPoint holds the last point reached; currChunkStartPoint is the start of this chunk
    finalChunkEndPoint = currPoint
    if currChunkStartPoint is not None and not np.array_equal(currChunkStartPoint, finalChunkEndPoint):
        rotation = chunkRotation(currChunkStartPoint, finalChunkEndPoint)
    else:
        rotation = 0.0  # Fallback: no meaningful direction

    currChunkPrintLoc[0] = currChunkPrintLoc[0] * pixelToCMWidth
    currChunkPrintLoc[1] = currChunkPrintLoc[1] * pixelToCmHeight
    printLocations.append([currChunkPrintLoc[0], currChunkPrintLoc[1], rotation])
    chunkRepList.append(currChunk)

    print("Length " + str(len(printLocations)))

    # Download all chunks as SVG
    count = 0
    for entry in chunkRepList:
        entry.save_svg(filename = "Chunk" + str(count))

        path = os.getcwd() + "/output/Chunk" + str(count) + ".svg"
        slice_svg(svg_path=path, output_path = "./output")
        count += 1

    # Convert all files to gcode files

    # Only display when debugging
    if __name__ == '__main__':
        plt.show()
    
    return printLocations

# For running this as main moduel for debugging run from root project dir as
# python -m flaskWebServer.printBedSlicer.processSVG
if __name__ == '__main__':
    # Only need os for testing
    import os
    print("Current executing directory " + str(os.getcwd()))
    print("Print testing function")
    filename = "testSVG/ZigZagLine.svg"
    with open(filename) as f:
        s = f.read()
        print(s)
        # Real potential dimmensions
        # Prusa bed size 33 length, 33 width
        sliceToPrintBed(s, 75, 75, 33, 33)