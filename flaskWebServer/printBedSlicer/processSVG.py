from svg.path import parse_path
from svg.path.path import Line
from svg.path.path import QuadraticBezier
from svg.path.path import CubicBezier
from xml.dom import minidom
from xml.dom.minidom import parse, parseString, Document
import matplotlib.pyplot as plt
import numpy as np

# Local imports
from rendering.chunkRepresentation import chunkRepresentation

def compPoint(p1, p2):
    status = p1[0] == p2[0] and p1[1] == p2[1]
    print(status)
    return status

def pointDist(p1, p2):
    return np.sqrt(np.square(p1[0] - p2[0]) + np.square(p1[1] - p2[1]))

def sliceToPrintBed(SVGFileInput: str, 
                    SVGWidthCM: int,
                    SVGHeightCM: int,
                    printBedWidthCM: int, 
                    printBedHeightCM: int):

    # read the SVG file
    domSVG = parseString(SVGFileInput)
    path_strings = [path.getAttribute('d') for path
                    in domSVG.getElementsByTagName('path')]
    
    # Get raw XML for easy manipulation of XML representation as well as easy transfering back
    # to XML at the end
    path_raw_xml = [path for path
                    in domSVG.getElementsByTagName('path')]
    
    # If these are different length we went wrong somewhere
    assert len(path_strings) == len(path_raw_xml)

    

    fig, ax = plt.subplots()
    fig.set_figheight(10)
    fig.set_figwidth(10)

    currPoint = [-1, -1]
    chunkRepList = []

    # Each chunk has it's own dedicated XML document that will be converted to XML later down the line
    currChunk = chunkRepresentation()
    
    # Draw the shape out on MatPlotLib
    iterator = 0
    for path_string in path_strings:
        path = parse_path(path_string)
        # Assume that there is only one element per path
        # Move to end of print bed
        printBedDistRemaining = printBedWidthCM

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

                # Handle cases
                # Line does not cover print bed
                if printBedDistRemaining - currPointEndLineDist > 0:
                    currLineXML = path_raw_xml[iterator]
                    currXMLChunkedLines.append(currLineXML)
                    printBedDistRemaining -= currPointEndLineDist
                    currPoint = np.array([x1, y1])

                elif printBedDistRemaining == 0:
                    # TODO End this chunk no need to bisect start on next line (Will handle this later)
                    pass

                # Line finished the rest of print bed, splice line at ending point,
                # manipulate next part of line to be spliced at end of print bed. 
                # Finally create print section using the finished chunks data for printer
                # Add ArUco marker as well
                else:
                    while (currPointEndLineDist > 0):
                        # Find bisection point
                        if currPointEndLineDist - printBedWidthCM < 0:
                            currPoint = np.array([x1, y1])
                            break

                        # Store current point for reference later
                        cachedCurrPoint = currPoint

                        # Get bisection point where the chunk ends
                        unit = (endPoint - startPoint) / pointDist(startPoint, endPoint)
                        bisect_point = currPoint + (unit * printBedDistRemaining)
                        print(bisect_point)
                        ax.plot(bisect_point[0], bisect_point[1], marker='o')
                        currPoint = bisect_point
                        print("Bisect " + str(bisect_point))
                        print(printBedDistRemaining)

                        # Update path tracing state
                        currPointEndLineDist -= printBedDistRemaining
                        printBedDistRemaining = printBedWidthCM

                        # Handle SVG
                        currChunk.appendLine(cachedCurrPoint[0], 
                                             cachedCurrPoint[1],
                                             bisect_point[0], 
                                             bisect_point[1])
                        currChunk.displayChunk()

                        # Reset chunk data and account for chunk
                        chunkRepList.append(currChunk)
                        currChunk = chunkRepresentation()
                        

        iterator += 1

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
        sliceToPrintBed(s, 1, 1, 10, 1)