# Object that contains reference to all of the controllers and data needed b
# other parts of the project. Intended to be a easy shortcut for passing 
# references to all essential objects at once

# NOTE: Might be more fitting to name this robot attributes instead of global state

# Local python script imports
import subModules.hardwareInterface.cameraConfig as cameraConfig
import subModules.hardwareInterface.roborockHighResInterface as roborockHighResInterface
from ..hardwareInterface.roborockCoordinateMoveInterface import roborockCoordinateMoveInterface
import subModules.hardwareInterface.controlRoborock as controlRoborock

import os
import sys
from dotenv import load_dotenv

from picamera2 import Picamera2

# Check openCV version
import cv2

class robotGlobalState:
        
    # Instantiates and creates all necessary references
    def __init__(self, 
               IP_ADDRESS: str, 
               API_KEY: str,
               headlessRunStatus: bool,
               performingAPICalls: bool,
               aruco_marker_side_length: int):
        if IP_ADDRESS is None or API_KEY is None or aruco_marker_side_length is None:
            raise Exception("roborock attribute not specifed")
        
        self.IP_ADDRESS_ = IP_ADDRESS
        self.API_KEY_ = API_KEY
        
        if headlessRunStatus is None:
            raise Exception("headlessRunStatus parameter not defined")
        self.headlessRunStatus_ = headlessRunStatus

        if performingAPICalls is None:
            raise Exception("performingAPICalls parameter not defined")
        self.performingAPICalls_ = performingAPICalls

        if aruco_marker_side_length is None:
            raise Exception("aruco_marker_side_length parameter not defined")
        self.arucoMarkerSideLength_ = aruco_marker_side_length 
        
        # If not using camera dont initiate
        if not headlessRunStatus:
            self.cameraReference_ = cameraConfig.configureCamera()

        self.roborockHighResInterfaceRef_ = roborockHighResInterface.roborockHighResInterface(IP_ADDRESS=IP_ADDRESS, API_KEY=API_KEY) 
        self.roborockCoordinateMoveInterfaceRef_ = roborockCoordinateMoveInterface(IP_ADDRESS=IP_ADDRESS, API_KEY=API_KEY)
        self.realWorldPathEstimationRef_ = realWorldPathEstimation()
        self.currPosCoordinate = None # Coordinates are stores in [X, Y] points in a cartesian plane where the center of the plane is the center
                                      # of the ARuco marker 0
        self.currRot = 0              # Rotation of the roborock relative to the first aruco marker


    def initiateRobotSubsystems(self):
        if self.performingAPICalls_:
            self.roborockHighResInterfaceRef_.initiateHighResManualControl()

    # Gracefully shutdown subsystems
    def stopRobotSubsystems(self):

        if self.performingAPICalls_:
            self.roborockHighResInterfaceRef_.disableHighResManualControl()

        self.cameraReference_.stop()

# Wrapper for pathObjRepresentation that contains similar data however will be estimated based
# on the orientation of the roborock and camera data
class realWorldPathEstimation(pathObjRepresentation):
    def __init__(self, finArucoVal):
        self.finArucoVal_ = finArucoVal

    
