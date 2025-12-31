from ..hardwareInterface.roborockHighResInterface import roborockHighResInterface
from ..hardwareInterface.roborockCoordinateMoveInterface import roborockCoordinateMoveInterface

class roborockGcodeParser:
    def __init__(self, roborockHighResInterface, gcodeFileName):
        with open('test.gcode', 'r') as file:
            if file is None:
                return
            content = file.read()

# For testing script
if __name__ == "__main__":

    print("test")
    