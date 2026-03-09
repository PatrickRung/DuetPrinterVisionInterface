from svg.path import parse_path
from svg.path.path import Line
from svg.path.path import QuadraticBezier
from svg.path.path import CubicBezier
from xml.dom import minidom
from xml.dom.minidom import parse, parseString, Document
import matplotlib.pyplot as plt
import numpy as np

# Local modules
from rendering import renderingHelper

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
    
    renderingHelper.display_svg(SVGFileInput)

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
    currXMLChunkedLines = []
    # List containing strings of SVG files that will be converted and sent to SVG -> GCode slicer
    SVGStrings = []

    # REWRITE
    # Iterate through path considering the chunks first, essentially keep popping lines until print bed is exhausted
    # for better chunking handling
    
    
    # Draw the shape out on MatPlotLib
    iterator = 0
    for path_string in path_strings:
        path = parse_path(path_string)
        # Assume that there is only one element per path
        # Move to end of print bed
        printBedDistRemaining = printBedWidthCM
        currChunkDoc = minidom.Document()

        while (printBedDistRemaining > 0):
            # Ran out of paths go to next loop to get more line distance
            if (len(path) == 0):
                break
            currElement = path.pop()
            print(type(currElement))

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
                    # Initiate temp doc for creating non linked path (no parent document)

                    pathRef = currChunkDoc.createElement("path")
                    path_data = f"M {cacheCurrPoint[0]} {cacheCurrPoint[1]} L {bisect_point[0]} {bisect_point[1]}"
                    pathRef.setAttribute("d", path_data)
                    pathRef.setAttribute("stroke", "#55ff00")

                    currXMLChunkedLines.append(pathRef)

                    printBedDistRemaining -= currPointEndLineDist
                    currPoint = np.array([x1, y1])

                elif printBedDistRemaining == 0:
                    # TODO End this chunk no need to bisect start on next line (Will handle this later)
                    pass

                # Case where print bed 
                else:
                    cacheCurrPoint = currPoint

                    # Find bisection point
                    unit = (endPoint - startPoint) / pointDist(startPoint, endPoint)
                    bisect_point = currPoint + (unit * printBedDistRemaining)
                    ax.plot(bisect_point[0], bisect_point[1], marker='o')
                    currPoint = bisect_point

                    # By bisecting a line we guarantee that this line has been cut into multiple lines
                    printBedDistRemaining = 0

                    # Append bisected lines
                    path_data = f"M {cacheCurrPoint[0]} {cacheCurrPoint[1]} L {bisect_point[0]} {bisect_point[1]}"
                    newBisectedPath = currChunkDoc.createElement("path")
                    newBisectedPath.setAttribute("d", path_data)
                    newBisectedPath.setAttribute("stroke", "#55ff00")
                    currXMLChunkedLines.append(newBisectedPath)

                    # Create <svg> root element
                    svg = currChunkDoc.createElement("svg")
                    svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
                    svg.setAttribute("width", str(100))
                    svg.setAttribute("height", str(100))
                    currChunkDoc.appendChild(svg)

                    # Add all lines into 
                    for line in currXMLChunkedLines:
                        svg.appendChild(line)

                    # Remove all data corresponding for current print bed to prepare for next bed
                    currXMLChunkedLines.clear()

                    xmlAsString = currChunkDoc.toprettyxml()
                    print("Current XML: " + str(xmlAsString))
                    renderingHelper.display_svg(xmlAsString)
                    print("chunk")

        iterator += 1
    
    # If there is left over chunk data append that to a chunk as well
    if len(currXMLChunkedLines) > 0:
        for line in currXMLChunkedLines:
            svg.appendChild(line)

        # Remove all data corresponding for current print bed to prepare for next bed
        currXMLChunkedLines.clear()

        xmlAsString = currChunkDoc.toprettyxml()
        print("Current XML: " + str(xmlAsString))
        renderingHelper.display_svg(xmlAsString)


    plt.show()
    # Process 

# printOrientation is the direction of the vector 
def processChunkData(self, printerOrientation):
    pass

if __name__ == '__main__':
    # Only need os for testing
    import os
    print("Current executing directory " + str(os.getcwd()))
    print("Print testing function")
    filename = "testSVG/ZigZagLine.svg"
    with open(filename) as f:
        s = f.read()
        sliceToPrintBed(s, 1, 1, 20, 1)