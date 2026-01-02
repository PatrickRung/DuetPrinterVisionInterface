from ..hardwareInterface.roborockHighResInterface import roborockHighResInterface
from ..hardwareInterface.roborockCoordinateMoveInterface import roborockCoordinateMoveInterface

import os

from dotenv import load_dotenv

# To run this file independently use the command below from the root direcotry:
# python3 -m subModules.printParsers.roborockGcodeParser
# This command is only run for testing purposes
class roborockGcodeParser:
    def __init__(self, 
                 roborockHighResInterfaceRef: roborockHighResInterface, 
                 roborockCoordinateMoveInterfaceRef : roborockCoordinateMoveInterface,
                 gcodeFileName):

        with open("gcodeFiles/" + gcodeFileName, 'r') as file:

            linesRef = file.readlines()

            for currLine in linesRef:
                print("Line: " + currLine)
                print("first letter of Line: " + currLine[0])

                # If the first letter for the command starts with a R, it must be a roborock commands
                # if the first letter does not start with an R it must be a regular Gcode command
                if currLine[0] == "R":

                    # Check what kind of roborock command it is
                    if currLine[1] == "M":
                        print("detect M character")
                        moveValue = int(currLine[2:])
                        print(moveValue)

                    if currLine[1] == "R":
                        rotValue = int(currLine[2:])
                        print(rotValue)

                    if currLine[1] == "A":
                        arucoValue = int(currLine[2:])
                        print(arucoValue)


# For testing script
if __name__ == "__main__":
    load_dotenv()

    # Roborock API key so that git stops complaining
    api_key = str(os.getenv("API_KEY"))
    IP_ADDRESS = str(os.getenv("IP_ADDRESS"))
    print("Address: " + api_key)

    roborockHighResInterfaceRef = roborockHighResInterface(IP_ADDRESS= IP_ADDRESS, API_KEY=api_key)
    roborockCoordinateMoevInterfaceRef = roborockCoordinateMoveInterface(IP_ADDRESS= IP_ADDRESS, API_KEY=api_key)

    gcodeParserRef = roborockGcodeParser(roborockHighResInterfaceRef, 
                                         roborockCoordinateMoevInterfaceRef, 
                                         "test.gcode")
    