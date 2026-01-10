

# Class attributes:

class PrintMainState:

    # starting coord is a tuple of length 2 being the xy coordinates relative to the first aruco marker (aruco marker 0)
    def __init__(self, startingCoord, initialPathObjRepresentation):

        if len(startingCoord) != 2:
            raise ValueError("Starting coord not of tuple length 2")
        self.startingCoord_ = startingCoord

        if not isinstance(initialPathObjRepresentation, pathObjRepresentation):
            raise TypeError("")

# This class is the predetermined approximation of where the aruco markers are and what aruco markers the roborock will have to pass through
# Can be used by a print parser to control the roborock
# Class attributes:
# finArucoVal: final aruco marker number, once the roborock runs into this value, all movements finish
# vectorBetweenArucoNodes: 2D vector representing the direction that the roborock needs to travel and how far 
#                          to get to the next aruco node in the sequence (Aruco markers value increase monotonically always)
class pathObjRepresentation:
    def __init__(self, finArucoVal, vectorBetweenArucoNodes):

        if not isinstance(finArucoVal, int):
            raise ValueError("finArucoVal is not of type int")
        self.finArucoVal_ = finArucoVal

        if not isinstance(vectorBetweenArucoNodes, tuple)
            raise TypeError("Expected vectorBetweenArucoNodes to be a tuple of 2D vectors")

        for vector in vectorBetweenArucoNodes:
            if not vector isinstance(vector, tuple) or len(vector) != 2:
                raise valueError("vector is not a compatible with coordinates (not a length 2 tuple)")
        
        self.vectorBetweenArucoNodes_ = vectorBetweenArucoNodes


