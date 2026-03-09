from xml.dom import minidom

# Local imports
from rendering.renderingHelper import display_svg

# State for specific chunks, can be translated into SVG representation
# when chunking is complete
class chunkRepresentation:

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
        # Create XML representation
        pathRef = self.docRef.createElement("path")
        path_data = f"M {x0} {y0} L {x1} {y1}"
        pathRef.setAttribute("d", path_data)
        pathRef.setAttribute("stroke", "#55ff00")

        self.currXMLChunkedLines.append(pathRef)

    def convertToSVG(self) -> str:
        svg = self.docRef.createElement("svg")
        svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
        svg.setAttribute("width", str(100))
        svg.setAttribute("height", str(100))
        
        for XMLLine in self.currXMLChunkedLines:
            svg.appendChild(XMLLine)

        return svg.toprettyxml()
    
    def displayChunk(self):
        svgString = self.convertToSVG()
        display_svg(svgString)


        
        
        