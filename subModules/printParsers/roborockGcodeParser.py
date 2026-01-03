from ..hardwareInterface.roborockHighResInterface import roborockHighResInterface
from ..hardwareInterface.roborockCoordinateMoveInterface import roborockCoordinateMoveInterface
import subModules.hardwareInterface.controlRoborock as controlRoborock
from ..robotState.robotGlobalState import robotGlobalState

import os

from dotenv import load_dotenv

# To run this file independently use the command below from the root direcotry:
# python3 -m subModules.printParsers.roborockGcodeParser
# This command is only run for testing purposes
class roborockGcodeParser:

    def __init__(self, robotGlobalStateRef: robotGlobalState):
        self.robotGlobalStateRef_ = robotGlobalStateRef

    def runGcodeFile(self, gcodeFileName):
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
                        self.robotGlobalStateRef_.roborockCoordinateMoveInterfaceRef_.moveLidarBased(moveValue)

                    if currLine[1] == "R":
                        rotValue = int(currLine[2:])
                        print(rotValue)
                        self.robotGlobalStateRef_.roborockCoordinateMoveInterfaceRef_.moveLidarBased(rotValue)

                    if currLine[1] == "A":
                        arucoValue = int(currLine[2:])
                        controlRoborock.moveToDesignatedArucoMarker(performingAPICalls=True, 
                                                                    localRoborockInterface=self.robotGlobalStateRef_.robo, 
                                                                    picam2= self.robotGlobalStateRef_.cameraReference_, 
                                                                    aruco_marker_side_length= self.robotGlobalStateRef_.arucoMarkerSideLength_, 
                                                                    desiredID=arucoValue, 
                                                                    headlessRunStatus=self.robotGlobalStateRef_.headlessRunStatus_,
                                                                    arucoAproxDirection=1)