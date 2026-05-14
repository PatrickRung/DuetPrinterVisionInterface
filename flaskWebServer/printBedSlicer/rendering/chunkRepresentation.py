# File contains objects of many of the common ways to describe chunks, multiple chunks
# or parts within the chunks such as lines and points.

from xml.dom import minidom
from abc import ABC, abstractmethod
import os

# Local imports (Use a . in front for relative dir imports)
from .renderingHelper import display_svg
import numpy as np

ARUCO_MARKER_LENGTH = 5
PRINTER_OFFSET = 20
LEN_THRESH = 18             # In CM, we need as too small leads to bad stl
# Printer offset mgiht be updated by the front end via API call, just be weary it's not a const

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

    def getLength(self):
        return np.linalg.norm(np.array([self.x0_, self.y0_]) - np.array([self.x1_, self.y1_]))

# State for specific chunks, can be translated into SVG representation
# when chunking is complete
class chunkRepresentation(XMLRep):

    def __init__(self, printBedWidthCM, printBedHeightCM):
        self.currXMLChunkedLines = []
        self.docRef = minidom.Document()

        # Print Bed Dims
        self.bedWidthCM = printBedWidthCM
        self.bedHeightCM = printBedHeightCM
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
        """
        Wraps up all data into final SVG
        """
        # Check if valid SVG (total length greater than print threshhold)

        total_len = 0
        for line in self.currXMLChunkedLines:
            total_len += line.getLength() 
        print("Chunk length" + str(total_len))
        if (total_len != LEN_THRESH):
            return ""

        svg = self.docRef.createElement("svg")
        svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")

        boundingMaxX = 0
        boundingMaxY = 0
        for currLineRepObj in self.currXMLChunkedLines:
            p0, p1 = currLineRepObj.getPoints()

            # Convert points from cm to mm
            p0_mm = p0 * 10
            p1_mm = p1 * 10

            pathRef = self.docRef.createElement("path")
            path_data = f"M {p0_mm[0]} {p0_mm[1]} L {p1_mm[0]} {p1_mm[1]}"
            pathRef.setAttribute("d", path_data)
            pathRef.setAttribute("stroke", "#55ff00")

            svg.appendChild(pathRef)

            boundingMaxX = np.max([boundingMaxX, p0_mm[0], p1_mm[0]])
            boundingMaxY = np.max([boundingMaxY, p0_mm[1], p1_mm[1]])

        # Set width/height in mm (converted from cm)
        svg.setAttribute("width", str(int(np.ceil(self.bedWidthCM * 10))))
        svg.setAttribute("height", str(int(np.ceil(self.bedHeightCM * 10))))

        # Append ArUco marker squares
        firstLine = self.currXMLChunkedLines[0]
        lineOneStart, lineOneEnd = firstLine.getPoints()
        lineOneStart = lineOneStart * 10
        lineOneEnd = lineOneEnd * 10

        lastLine = self.currXMLChunkedLines[len(self.currXMLChunkedLines) - 1]
        lineTwoStart, lineTwoEnd = lastLine.getPoints()
        lineTwoStart = lineTwoStart * 10
        lineTwoEnd = lineTwoEnd * 10

        # Compute direction vector from lineOneStart -> lineTwoEnd, then rotate 90° CCW
        # to place markers outside (to the left of) the line set
        dir_vec = lineTwoEnd - lineOneStart
        dir_len = np.linalg.norm(dir_vec)
        if dir_len > 0:
            dir_vec = dir_vec / dir_len

        # Rotate offset might need to be cw or ccw depending on print bed orientation
        perp_vec = np.array([dir_vec[1], -dir_vec[0]])
        ARUCO_MARKER_LENGTH_MM = ARUCO_MARKER_LENGTH * 10
        offset = perp_vec * ARUCO_MARKER_LENGTH_MM

        # Marker at lineOneStart: offset outward so the square sits outside the lines
        marker1_x = lineOneStart[0] + offset[0] - ARUCO_MARKER_LENGTH_MM / 2
        marker1_y = lineOneStart[1] + offset[1] - ARUCO_MARKER_LENGTH_MM / 2

        # Marker at lineTwoEnd: same outward offset
        marker2_x = lineTwoEnd[0] + offset[0] - ARUCO_MARKER_LENGTH_MM / 2
        marker2_y = lineTwoEnd[1] + offset[1] - ARUCO_MARKER_LENGTH_MM / 2

        for marker_x, marker_y in [(marker1_x, marker1_y), (marker2_x, marker2_y)]:
            validX, validY = self.moveIntoBounds(marker_x, marker_y)
            rectRef = self.docRef.createElement("rect")
            rectRef.setAttribute("x", str(validX))
            rectRef.setAttribute("y", str(validY))
            rectRef.setAttribute("width", str(ARUCO_MARKER_LENGTH_MM))
            rectRef.setAttribute("height", str(ARUCO_MARKER_LENGTH_MM))
            rectRef.setAttribute("stroke", "#55ff00")
            rectRef.setAttribute("fill", "none")
            svg.appendChild(rectRef)

        # TODO store state in some kind of data store for reference in 2nd pass backend control path

        # Print for debugging purposes
        res = svg.toprettyxml()
        print("res: " + res)
        return res

    def save_svg(self, output_dir: str = "./output", filename: str = "output") -> str:
        """
        Calls toSVG() and saves the resulting SVG to a local directory.
        
        Args:
            output_dir: Directory to save the SVG file (created if it doesn't exist)
            filename:   Optional filename (without extension). Defaults to 'output'.
        
        Returns:
            The full path to the saved file.
        """
        svg_content = self.toSVG()

        if (svg_content == ""):
            return ""

        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, f"{filename}.svg")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)

        print(f"SVG saved to: {filepath}")
        return filepath
    
    def displayChunk(self):
        svgString = self.toSVG()
        display_svg(svgString)

    def reorientInPrintSpace(self, pixelToCMWidth, pixelToCmHeight):
        """
        Takes in the angle that the 3D printer is facing towards when it performs the 3D printer 
        (Essentially the angle of the vector from the )

        paramters:
            angle: angle in radians of the robot when it prints at this location
        """

        # Find angle according to start and end of line segments
        firstLine = self.currXMLChunkedLines[0]
        lineOneStart, lineOneEnd = firstLine.getPoints()

        lastLine = self.currXMLChunkedLines[len(self.currXMLChunkedLines) - 1]
        lineTwoStart, lineTwoEnd = lastLine.getPoints()

        dx = lineTwoEnd[0] - lineOneStart[0]
        dy = lineTwoEnd[1] - lineOneStart[1]

        angle = np.atan2(dy, dx)  # radians
        angle += np.pi * 2

        rotMatrix = np.array([[np.cos(angle), -np.sin(angle)], 
                              [np.sin(angle), np.cos(angle)]])
        minX = 0
        minY = 0

        # Rotate to new rotation space
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

        # Collect unique points (avoid double-counting shared endpoints between lines):
        # include p0 for every line, and only p1 for the very last line
        unique_points = []
        for idx, currLineRepObj in enumerate(self.currXMLChunkedLines):
            p0, p1 = currLineRepObj.getPoints()
            unique_points.append(p0)
            if idx == len(self.currXMLChunkedLines) - 1:
                unique_points.append(p1)

        centroid = np.mean(unique_points, axis=0)

        # Convert to CM space centered at origin first
        svg_center = np.array([self.bedWidthCM / 2.0, self.bedHeightCM / 2.0])

        # Subtract centroid to center the shape, convert to CM space, then shift to SVG center
        for currLineRepObj in self.currXMLChunkedLines:
            p0, p1 = currLineRepObj.getPoints()

            newP0 = (p0 - centroid) * np.array([pixelToCMWidth, pixelToCmHeight]) + svg_center
            currLineRepObj.updateP0(newP0)

            newP1 = (p1 - centroid) * np.array([pixelToCMWidth, pixelToCmHeight]) + svg_center
            currLineRepObj.updateP1(newP1)

    def moveIntoBounds(self, topLeftX, topLeftY):
        '''
        For moving ArUco square in bounds (all units in mm)
        '''

        newX = topLeftX
        newY = topLeftY

        if topLeftX < 0:
            newX = 0
        if topLeftY < 0:
            newY = 0

        bedWidthMM = self.bedWidthCM * 10
        bedHeightMM = self.bedHeightCM * 10
        ARUCO_MARKER_LENGTH_MM = ARUCO_MARKER_LENGTH * 10

        if (topLeftX + ARUCO_MARKER_LENGTH_MM > bedWidthMM):
            newX = bedWidthMM - ARUCO_MARKER_LENGTH_MM
        if (topLeftY + ARUCO_MARKER_LENGTH_MM > bedHeightMM):
            newY = bedHeightMM - ARUCO_MARKER_LENGTH_MM  # was incorrectly assigning to newX

        return newX, newY
    
    # Get and return desired print location based on the points added to the 
    def getPrintLocation(self):
        firstLine = self.currXMLChunkedLines[0]
        secondLine = self.currXMLChunkedLines[-1]

        # Direction vector along the line
        dirVector = np.array([secondLine.x1_ - firstLine.x0_, 
                            secondLine.y1_ - firstLine.y0_])

        # Normalize direction first
        dirMag = np.linalg.norm(dirVector)
        dirUnit = dirVector / dirMag

        # Perpendicular unit vector (rotate 90 degrees)
        perpUnit = np.array([dirUnit[1], -dirUnit[0]])

        # True midpoint
        centerLoc = np.array([
            (firstLine.x0_ + secondLine.x1_) / 2,
            (firstLine.y0_ + secondLine.y1_) / 2
        ])

        return centerLoc
        