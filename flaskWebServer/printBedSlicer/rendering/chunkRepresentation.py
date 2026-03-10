from xml.dom import minidom
from abc import ABC, abstractmethod

# Local imports
from rendering.renderingHelper import display_svg
import numpy as np

class XMLRep:

    @abstractmethod
    def toSVG(self):
        raise "Should implement to SVG function"


class lineRepresentation(XMLRep):
    def __init__(self, x0, y0, x1, y1):
        self.currXMLChunkedLines = []
        self.docRef = minidom.Document()

        self.x0_ = x0
        self.y0_ = y0
        self.x1_ = x1
        self.y1_ = y1

    def getPoints(self):
        """
        get two numpy arrays that represent the start and end point respectfully
        """
        return np.array([self.x0_, self.y0_]), np.array([self.x1_, self.y1_])

    def updateP0(self, point):
        self.x0_ = point[0]
        self.y0_ = point[1]

    def updateP1(self, point):
        self.x1_ = point[0]
        self.y1_ = point[1]

# State for specific chunks, can be translated into SVG representation
# when chunking is complete
class chunkRepresentation(XMLRep):

    def __init__(self):
        self.currXMLChunkedLines = []
        self.docRef = minidom.Document()
        pass

    # Add line from point x to point y
    def appendLine(self, x0, y0, x1, y1):
        """
        Appends line given the coordinates of two points. Forms a line going from
        point 0 -> point 1
        """
        # create line rep object
        self.currXMLChunkedLines.append(lineRepresentation(x0, y0, x1, y1))

    def toSVG(self) -> str:
        svg = self.docRef.createElement("svg")
        svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")

        boundingMaxX = 0
        boundingMaxY = 0
        for currLineRepObj in self.currXMLChunkedLines:
            p0, p1 = currLineRepObj.getPoints()

            pathRef = self.docRef.createElement("path")
            path_data = f"M {p0[0]} {p0[1]} L {p1[0]} {p1[1]}"
            pathRef.setAttribute("d", path_data)
            pathRef.setAttribute("stroke", "#55ff00")

            svg.appendChild(pathRef)

            boundingMaxX = np.max([boundingMaxX, p0[0], p1[0]])
            boundingMaxY = np.max([boundingMaxY, p0[1], p1[1]])
        
        # Set attribute and ensure that we set to base 64
        svg.setAttribute("width", str(int(np.ceil(boundingMaxX))))
        svg.setAttribute("height", str(int(np.ceil(boundingMaxY))))

        res  = svg.toprettyxml()
        print("res: " + res)
        return res
    
    def displayChunk(self):
        svgString = self.toSVG()
        display_svg(svgString)

    def reorientInPrintSpace(self, angle):
        """
        Takes in the angle that the 3D printer is facing towards when it performs the 3D printer 
        (Essentially the angle of the vector from the )

        paramters:
            angle: angle in radians of the robot when it prints at this location
        """

        rotMatrix = np.array([[np.cos(angle), -np.sin(angle)], 
                              [np.sin(angle), np.cos(angle)]])
        minX = 0
        minY = 0
        for currLineRepObj in self.currXMLChunkedLines:
            p0, p1 = currLineRepObj.getPoints()

            # Translate to rotated frame
            newP0 = np.matmul(p0, rotMatrix)
            currLineRepObj.updateP0(newP0)

            if minX == 0 and minY == 0:
                minX = newP0[0]
                minY = newP0[1]

            newP1 = np.matmul(p1, rotMatrix)
            currLineRepObj.updateP1(newP1)

            # Check for min values
            minX = np.min([minX, newP0[0], newP1[0]])
            minY = np.min([minY, newP0[1], newP1[1]])

        # Move all points to positive positions
        for currLineRepObj in self.currXMLChunkedLines:
            p0, p1 = currLineRepObj.getPoints()

            newP0 = p0 - np.array([minX, minY])
            currLineRepObj.updateP0(newP0)

            newP1 = p1 - np.array([minX, minY])
            currLineRepObj.updateP1(newP1)

        


        
        
        