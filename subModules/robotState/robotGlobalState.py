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

    # Instantiates with all necescary objects and variables and terminates program if this does not happen
    def __init__(self, 
                 cameraReference: Picamera2,
                 roborockHighResInterfaceRef: roborockHighResInterface,
                 roborockCoordinateMoveInterfaceRef: roborockCoordinateMoveInterface,
                 headlessRunStatus: bool,
                 performingAPICalls: bool,
                 aruco_marker_side_length: int):
        if cameraReference is None:
            raise Exception("cameraReference parameter not defined")
            sys.exit
        self.cameraReference_ = cameraReference
        
        if roborockHighResInterfaceRef is None:
            raise Exception("roborockHighResInterfaceRef parameter not defined")
        self.roborockHighResInterfaceRef_ = roborockHighResInterfaceRef

        if roborockCoordinateMoveInterfaceRef is None:
            raise Exception("roborockCoordinateMoveInterfaceRef parameter not defined")
        self.roborockCoordinateMoveInterfaceRef_ = roborockCoordinateMoveInterfaceRef

        if headlessRunStatus is None:
            raise Exception("headlessRunStatus parameter not defined")
        self.headlessRunStatus_ = headlessRunStatus

        if performingAPICalls is None:
            raise Exception("performingAPICalls parameter not defined")
        self.performingAPICalls_ = performingAPICalls

        if aruco_marker_side_length is None:
            raise Exception("aruco_marker_side_length parameter not defined")
        self.arucoMarkerSideLength_ = aruco_marker_side_length 
        
    # Instantiates and creates all necessary references
    def __init(self, 
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
        
        self.cameraReference_ = cameraConfig.configureCamera()
        self.roborockHighResInterfaceRef_ = roborockHighResInterface.roborockHighResInterface(IP_ADDRESS=IP_ADDRESS, API_KEY=API_KEY) 
        self.roborockCoordinateMoveInterfaceRef_ = roborockCoordinateMoveInterface(IP_ADDRESS=IP_ADDRESS, API_KEY=API_KEY)


    def initiateRobotSubsystems(self):
        if self.performingAPICalls_:
            self.roborockHighResInterfaceRef_.initiateHighResManualControl()

    # Gracefully shutdown subsystems
    def stopRobotSubsystems(self):

        if self.performingAPICalls_:
            self.roborockHighResInterfaceRef_.disableHighResManualControl()

        self.cameraReference_.stop()

