import sys
sys.path.append('..')
import keyboard

# Local Classes
from ..hardwareInterface.roborockInterface import roborockInterface
import arucoHandling

# For Open CV
import cv2
import numpy

# State management
from enum import Enum
from time import perf_counter
import time

# Resource management data
import psutil

class roborockMoveState(Enum):

    # State where roborock does not know where aruco marker is thus it must search surroundings by rotating
    LOOKING_FOR_ARUCO_MARKER = 0

    # Aruco marker located, the roborock must now move towards target
    MOVE_TOWARD_ARUCO_MARKER = 1

    # Aruco was or is in view, roborock must now move backwards if it went too far, correct its angle
    # Once this state is held for more than 2 seconds we finished arriving at the destination
    REACHED_DESTINATION_UNDERGOING_VERIFICATION = 2

    # Aruco marker is in view and stable due to being in view for 2 seconds, exit loop
    DEST_REACHED_CONFIRM = 3

class perfClock:
    perfTimerStart_ = 0
    length_ = 0
    timeElapsed_ = 0

    def __init__(self, length):
        self.length_ = length
        self.perfTimerStart_ = perf_counter()
        self.timeElapsed_ = 0

    # Increment timer, and check whether the timer length has expired
    def pollIncrementTime(self):
        self.timeElapsed_ = perf_counter() - self.perfTimerStart_
        
        if self.timeElapsed_ > self.length_:
            return True
        return False

    def resetTimer(self):
        self.perfTimerStart_ = perf_counter()
        self.timeElapsed_ = 0

class frameRateTracker:
    lastPollTimeStamp = 0

    def getPollingFrameRate(self):
        if self.lastPollTimeStamp == 0:
            self.lastPollTimeStamp = perf_counter()
            return 0
        timeSinceLastPoll = perf_counter() - self.lastPollTimeStamp
        self.lastPollTimeStamp = perf_counter()
        print("time val " + str(timeSinceLastPoll))
        return numpy.round(1.0 / timeSinceLastPoll, 0)
    


# The range that aruco markers can be detected in meters from the closest that the camera can deetect
# Aruco markers to the farthest distance that is still considered satisfactory for stopping.
satisfactoryRange = 0.15

# Default distance from base of camera to edge of detecting Aruco markes. Determined by testing
defaultCamBaseDist = 0.25

# Given a translation vector from the camera to the aruco marker, return
# the value of the distance between the base of the roborock to the aruco marker
# Assumes that the Aruco marker is flat on the ground
# World space variables are lablex where x is forward: + backward: -
# y is right: + left: -
def getWorldspaceDistance(tvec, rvec):

    angleRelativeToRoborock = (numpy.pi / 2) - get_camera_pivot_rot(rvec)

    # Get world space X magnitude of the Z component of the camera to Aruco translation vector 
    camSpaceZToWorldSpaceX = tvec[2] * numpy.cos(angleRelativeToRoborock)

    # Get world space X magnitude of the Y component of the camera to Aruco translation vector 
    camSpaceYToWorldSpaceX = tvec[1] * numpy.cos(angleRelativeToRoborock)

    distArucoToBaseOfRoborock = numpy.abs(camSpaceZToWorldSpaceX) - numpy.abs(camSpaceYToWorldSpaceX)

    return distArucoToBaseOfRoborock

# Return camera pivot in rad
# Returns angel relative to line parallel to the arm holding the camera
def get_camera_pivot_rot(rvec):
    # Convert rotation vector to rotation matrix
    cameraMarkerMatrix, _ = cv2.Rodrigues(rvec)

    # Invert rotation (transpose)
    InverseCameraMarkerMatrix = cameraMarkerMatrix.T

    sy = numpy.sqrt(InverseCameraMarkerMatrix[0,0]**2 + InverseCameraMarkerMatrix[1,0]**2)
    singular = sy < 1e-6

    if not singular:
        pivotRot  = numpy.arctan2(InverseCameraMarkerMatrix[2,1], InverseCameraMarkerMatrix[2,2])
    else:
        pivotRot  = numpy.arctan2(-InverseCameraMarkerMatrix[1,2], InverseCameraMarkerMatrix[1,1])

    if pivotRot < 0:
        pivotRot += numpy.pi

    return pivotRot
    
# Function assumes that the aruco marker is within view
# if aruco aprox directinon is > 0, that signifies the roborock should rotate to the right 
# to find the next aruco marker, if the aprox direction is < 0, then the roborock turns left
def moveToDesignatedArucoMarker(performingAPICalls, 
                                localRoborockInterface, 
                                picam2, 
                                aruco_marker_side_length, 
                                desiredID, 
                                headlessRunStatus, 
                                arucoAproxDirection):
    # Calibration parameters yaml file
    camera_calibration_parameters_filename = 'calibration_chessboard.yaml'

    # Load the camera parameters from the saved file
    cv_file = cv2.FileStorage(
        camera_calibration_parameters_filename, cv2.FILE_STORAGE_READ) 
    mtx = cv_file.getNode('K').mat()
    dst = cv_file.getNode('D').mat()
    cv_file.release()

    aruco_mark_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    arucoHandling.generate_aruco_images(aruco_mark_dict)
    det_param = cv2.aruco.DetectorParameters()

    currentRobotMoveState = roborockMoveState.LOOKING_FOR_ARUCO_MARKER
    print("restart state")

    # The amount that angle from the center of the camera and the aruco marker can be off by
    # any less than or greater than this amount will cause a rotation correction
    rotationMarginOfError = 4

    # Create the Aruco detector before running loop
    detector = cv2.aruco.ArucoDetector(aruco_mark_dict, det_param)

    # Declared null on init however is asigned to a timer object when finsihed
    reachedDestVerificationTimer = None

    localFrameRateTracker = frameRateTracker()

    # Main loop for handling detection
    while True:
        frame = picam2.capture_array()
        print("Desired ID: " + str(desiredID))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = detector.detectMarkers(gray)

        # Commented out to check whether frame rate tracking is the issue 
        currentFrameRate = localFrameRateTracker.getPollingFrameRate()

        cv2.putText(frame, str("FPS: ") + str(currentFrameRate), (7, 70), cv2.FONT_HERSHEY_PLAIN, 2, (100, 255, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, str("CPU: ") + str(psutil.cpu_percent()) + str("%"), (7, 100), cv2.FONT_HERSHEY_PLAIN, 2, (100, 255, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, str("RAM: ") + str(psutil.virtual_memory().percent) + str("%"), (7, 130), cv2.FONT_HERSHEY_PLAIN, 2, (100, 255, 0), 3, cv2.LINE_AA)

        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        if not headlessRunStatus:
            print("this happen")
            cv2.imshow("Frame", frame)
        else:
            print("in headless run")

        # This conditional is required for polling cv2 frames
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Gracefully shutting down")
            break
    
        print(currentRobotMoveState)

        # Get index of Aruco with desired ID
        arucoIndex = -1
        iterator = 0
        if ids is not None:
            for ArucoID in ids:
                if ArucoID == desiredID:
                    arucoIndex = iterator
                iterator += 1



        # Perform operation based on state
        if currentRobotMoveState == roborockMoveState.LOOKING_FOR_ARUCO_MARKER:
            # Roborock rotate to find next aruco marker
            if arucoIndex == -1:
                if performingAPICalls:
                    if arucoAproxDirection > 0:
                        localRoborockInterface.moveVectored(0, 10)
                    else:
                        localRoborockInterface.moveVectored(0, -10)
                    print(ids)
                    time.sleep(2)
            else:
                currentRobotMoveState = roborockMoveState.MOVE_TOWARD_ARUCO_MARKER
                print("test")

        elif currentRobotMoveState == roborockMoveState.MOVE_TOWARD_ARUCO_MARKER:
            if arucoIndex != -1:
                rvecs, tvecs, obj_points = cv2.aruco.estimatePoseSingleMarkers(
                    corners,
                    aruco_marker_side_length,
                    cameraMatrix=mtx,
                    distCoeffs=dst)

                # inverse_marker_to_camera = numpy.linalg.inv(R_marker_to_camera)

                # print(inverse_marker_to_camera)

                # Calculate angle to turn to using tvec
                zMag = tvecs[arucoIndex][0][2]
                xMag = tvecs[arucoIndex][0][0]
                desiredAngle = numpy.rad2deg(numpy.arctan(xMag / zMag))

                # Calculate distance offset
                roborockArucoOffset = getWorldspaceDistance(tvec=tvecs[arucoIndex][0], rvec=rvecs[arucoIndex][0])

                print("Dist: " + str(roborockArucoOffset))
                
                if desiredAngle > rotationMarginOfError or desiredAngle < -rotationMarginOfError:
                    print("change angle")
                    if performingAPICalls:
                        localRoborockInterface.moveVectored(0, desiredAngle / 2)
                # Goal is to get the roborock within 16 cm of the Aruco marker
                elif roborockArucoOffset < defaultCamBaseDist + satisfactoryRange:
                    print("Fin")
                    currentRobotMoveState = roborockMoveState.REACHED_DESTINATION_UNDERGOING_VERIFICATION
                else:
                    print("moveForward")
                    # For the purpose of my initial testing this is reversed
                    if performingAPICalls:
                        localRoborockInterface.moveVectored(0.1, 0)
                        # Give some time for Roborock to coorect
                        cv2.waitKey(200)
        elif currentRobotMoveState == roborockMoveState.REACHED_DESTINATION_UNDERGOING_VERIFICATION:
            # Keep polling for 2 seconds to verify that Aruco marker is within view

            if ids is not None and desiredID in ids:
                    if reachedDestVerificationTimer is None:
                        reachedDestVerificationTimer = perfClock(length=2)
                    elif reachedDestVerificationTimer.pollIncrementTime():
                        currentRobotMoveState = roborockMoveState.DEST_REACHED_CONFIRM
                        print("done")
                        break
            else:
                print("moved too far")
                # Reset timer and move roborock back until marker is in view
                reachedDestVerificationTimer = None
                if performingAPICalls:
                    localRoborockInterface.moveVectored(-0.1, 0)
                    # Give time for camera to readjust
                    cv2.waitKey(20)