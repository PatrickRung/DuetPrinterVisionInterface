from ..hardwareInterface.roborockHighResInterface import roborockHighResInterface
from ..hardwareInterface.roborockCoordinateMoveInterface import roborockCoordinateMoveInterface
import subModules.hardwareInterface.controlRoborock as controlRoborock
from ..robotState.robotGlobalState import robotGlobalState
from ..robotState.printState import pathObjRepresentation
from ..constants import constants

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
                        controlRoborock.moveToDesignatedArucoMarker(self.robotGlobalStateRef_, 
                                                                    desiredID=arucoValue,
                                                                    arucoAproxDirection=1)

    # TODO needs to consider case where the aruco marker is out of range and needs to have hardcoded rotation that happen
    # to place next aruco marker approximately in view
    def runRoborockFromObjPathRef(self, path: pathObjRepresentation): 

        self.robotGlobalStateRef_.initiateRobotSubsystems()
        
        # We assume that the first aruco marker 0, is already in view when we start the program.
        # And that the aruco marker is directly in front of robot (straight path to marker)
        for currArucoMarker in range(0, path):

            if currArucoMarker == 0:
                controlRoborock.moveToDesignatedArucoMarker(self.robotGlobalStateRef_, 
                                                            desiredID=currArucoMarker,
                                                            arucoAproxDirection=1)
                # TODO tune parameter to get roborock to move directly over the Aruco marker
                self.robotGlobalStateRef_.roborockCoordinateMoveInterfaceRef_.moveLidarBased(constants.CAMERA_RANGE_LIMIT_ARUCO_DISTANCE)
                
            elif:
                # If not the first marker, there is chance that marker is out of view, thus
                # we must figure out where it is

                # TODO move to general direction of marker and move toward the object
                





