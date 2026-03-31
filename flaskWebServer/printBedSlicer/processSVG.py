from svg.path import parse_path
from svg.path.path import Line
from svg.path.path import QuadraticBezier
from svg.path.path import CubicBezier
from xml.dom import minidom
from xml.dom.minidom import parse, parseString, Document
import matplotlib.pyplot as plt
import numpy as np

# Local imports (Use a . in front for relative dir imports)
from .rendering.chunkRepresentation import chunkRepresentation

def compPoint(p1, p2):
    status = p1[0] == p2[0] and p1[1] == p2[1]
    print(status)
    return status

def pointDist(p1, p2):
    return np.sqrt(np.square(p1[0] - p2[0]) + np.square(p1[1] - p2[1]))

# The SVG will fit the entire size of the bed size.
def sliceToPrintBed(SVGFileInput: str, 
                    SVGWidthCM: int,
                    SVGHeightCM: int,
                    printBedWidthCM: int, 
                    printBedHeightCM: int):

    # read the SVG file
    domSVG = parseString(SVGFileInput)
    svgRef = domSVG.getElementsByTagName('svg')

    pixelWidth = svgRef[0].getAttribute('width')
    pixelHeight = svgRef[0].getAttribute('width')
    
    path_strings = [path.getAttribute('d') for path
                    in domSVG.getElementsByTagName('path')]
    
    # Get raw XML for easy manipulation of XML representation as well as easy transfering back
    # to XML at the end
    path_raw_xml = [path for path
                    in domSVG.getElementsByTagName('path')]
    
    # If these are different length we went wrong somewhere
    assert len(path_strings) == len(path_raw_xml)

    # Multiply any pixel value against these values to get the CM width
    pixelToCMWidth = SVGWidthCM / int(pixelWidth)
    pixelToCmHeight = SVGHeightCM / int(pixelHeight)

    fig, ax = plt.subplots()
    fig.set_figheight(10)
    fig.set_figwidth(10)

    currPoint = [-1, -1]
    chunkRepList = []

    # Each chunk has it's own dedicated XML document that will be converted to XML later down the line
    currChunk = chunkRepresentation(printBedWidthCM, printBedHeightCM)
    
    # Draw the shape out on MatPlotLib
    iterator = 0
    printBedDistRemaining = printBedWidthCM
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

                currPointEndLineDist = pointDist(currPoint, np.array([x1, y1]))

                while (currPointEndLineDist > 0):
                    # Find bisection point
                    currPointEndLineDist = pointDist(currPoint, np.array([x1, y1]))
                    if currPointEndLineDist - printBedWidthCM < 0:
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
                    ax.plot(bisect_point[0], bisect_point[1], marker='o')
                    currPoint = bisect_point

                    # Update path tracing state
                    printBedDistRemaining = printBedWidthCM

                    # Handle SVG
                    currChunk.appendLine(cachedCurrPoint[0], 
                                            cachedCurrPoint[1],
                                            bisect_point[0], 
                                            bisect_point[1])

                    # Reset chunk data and account for chunk
                    chunkRepList.append(currChunk)
                    currChunk.reorientInPrintSpace(pixelToCMWidth, pixelToCmHeight)
                    currChunk.displayChunk()
                    # currChunk.displayChunk()
                    currChunk = chunkRepresentation(printBedWidthCM, printBedHeightCM)

        iterator += 1

    # Only display when debugging
    if __name__ == '__main__':
        plt.show()
    # Process chunks

if __name__ == '__main__':
    # Only need os for testing
    import os
    print("Current executing directory " + str(os.getcwd()))
    print("Print testing function")
    filename = "testSVG/ZigZagLine.svg"
    with open(filename) as f:
        s = f.read()

        # Real potential dimmensions
        # Prusa bed size 33 length, 33 width
        sliceToPrintBed(s, 75, 75, 33, 33)