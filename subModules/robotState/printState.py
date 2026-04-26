

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
# roborockInstructions: A vector containing instances of roborockInstruction
class pathObjRepresentation:
    def __init__(self, finArucoVal, roborockInstructions):

        if not isinstance(finArucoVal, int):
            raise ValueError("finArucoVal is not of type int")
        self.finArucoVal_ = finArucoVal

        if not isinstance(roborockInstructions, tuple):
            raise TypeError("Expected vectorBetweenArucoNodes to be a tuple of 2D vectors")

        for vector in roborockInstructions:
            if not vector and isinstance(vector, tuple) or len(vector) != 2:
                raise ValueError("vector is not a compatible with coordinates (not a length 2 tuple)")
        
        self.roborockInstructions_ = roborockInstructions

# Base representation of a single pathObj instruction
# Classified as a null instruction (Will not throw error but will skip this empty instruction)
class roborockInstruction:
    pass

class roborockMoveForwardLidarBased(roborockInstruction):
    # Params:
    # dist = Distance in CM for roborock to move
    def __init__(self, dist):
        self.dist_ = dist 


class roborockMoveToArucoMarker(roborockInstruction):
    # Params:
    # ArUcoID = desired ArUcoID to move to
    # aproxDir = whether the aruco marker should be expected to appear to the left or right of the Roborocks
    # current orientation
    def __init__(self, ArUcoID, aproxDir):
        self.ArUcoID_ = ArUcoID
        self.aproxDir_ = aproxDir

class roborockRotateLidarBased(roborockInstruction):
    # Params:
    # dist = Distance in CM for roborock to move
    def __init__(self, rotation):
        self.rotation_ = rotation
    pass




