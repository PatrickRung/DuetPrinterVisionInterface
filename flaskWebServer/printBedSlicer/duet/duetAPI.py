#!/usr/bin/env python3
import sys
import os
import dsf
import json
import time
import shutil
import arucoHandling
from picamera2 import Picamera2

from dsf.connections import CommandConnection
from ..gcodeslice import slice_svg
from pathlib import Path

# For Open CV
import cv2
import numpy

import numpy as np
from scipy.spatial.transform import Rotation

# CONSTANTS
# TODO this should be a larger number however for testing i set it to 10
ID_IN_VIEW_THRESHOLD = 10 # How many pose estimation data points before we finish localizing
REF_ID = 23 # How many pose estimation data points before we finish localizing

def configureCamera() -> Picamera2:
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    return picam2

DSF_SD_DIR = "/opt/dsf/sd/gcodes"   # File found by searching sys for config.g

# Declare to none in case where we are debugging isolated slicer
command_connection = None

# Try to create upon creation of program (Timeout really big so we know when print done)
try:
    command_connection = CommandConnection(debug=True, timeout=1000000)
    if command_connection:
        command_connection.connect()
except:
    print("Duet board not connected right now!")

# Global store
printer_status = "idle"

def send_simple_code():
    
    if command_connection:

        try:
            # res = command_connection.set_plugin_data("ExecOnMcode", "test", "1")
            # Perform a simple command and wait for its output
            res = command_connection.perform_simple_code("M115")
            print("M115 is telling us:", res)
        finally:
            command_connection.close()
    res = command_connection.perform_simple_code("G28")

def home_printer():
    if command_connection:
        command_connection.connect()
    res = command_connection.perform_simple_code("G28")
    
# Assume that this function takes in a SVG path, then reorients that SVG in the proper bed space
def localize_slice_print(fileName: str, marker_length: float, ID1: float, ID2: float):
    """
    Uploads a gcode file and starts printing it using only the DSF CommandConnection.
    
    :param file_path: Local path to the .gcode file to upload
    """

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

    camera_ref = configureCamera()

    detector = cv2.aruco.ArucoDetector(aruco_mark_dict, det_param)

    # Loop until enough posoe estimation points have been recorded for both points
    IDS_in_view = 0

    translational_offset_vectors = []
    translational_rotation_vectors = []

    while IDS_in_view < ID_IN_VIEW_THRESHOLD:
        frame = camera_ref.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = detector.detectMarkers(gray)

        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # If running as main proc, we are debugging CV and thus need frame
        if __name__ == "__main__":
            cv2.imshow("Frame", frame)

        # This conditional is required for polling cv2 frames
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Gracefully shutting down")
            break

        # Get index of Aruco with desired ID
        arucoIndex = -1
        if ids is not None:
            iterator = 0

            ref_rvec = None
            ref_tvec = None
            eval_rvec = None
            eval_tvec = None

            # Estimate poses once for all detected markers
            rvecs, tvecs, obj_points = cv2.aruco.estimatePoseSingleMarkers(
                corners,
                marker_length,
                cameraMatrix=mtx,
                distCoeffs=dst)

            for ArucoID in ids:
                aid = int(ArucoID[0])  # ids is shaped (N,1), unwrap it

                if aid == REF_ID:
                    print("Found REF marker")
                    ref_rvec = rvecs[iterator]
                    ref_tvec = tvecs[iterator]

                if aid == ID1:
                    IDS_in_view += 1
                    eval_rvec = rvecs[iterator]
                    eval_tvec = tvecs[iterator]

                if aid == ID2:

                    eval_rvec = rvecs[iterator]
                    eval_tvec = tvecs[iterator]

                iterator += 1

            # --- Compute eval pose relative to ref marker ---
            if ref_rvec is not None and eval_rvec is not None:
                IDS_in_view += 1 # Add another data point
                # Convert rvecs to 3x3 rotation matrices
                R_ref,  _ = cv2.Rodrigues(ref_rvec)
                R_eval, _ = cv2.Rodrigues(eval_rvec)

                # Relative rotation: R_rel = R_ref^T * R_eval
                R_rel = R_ref.T @ R_eval

                # Relative translation: t_rel = R_ref^T * (t_eval - t_ref)
                t_rel = R_ref.T @ (eval_tvec.T - ref_tvec.T)

                # Convert relative rotation back to Rodrigues vector (axis-angle)
                rvec_rel, _ = cv2.Rodrigues(R_rel)

                print("Relative translation (eval w.r.t. ref):", t_rel.T)
                print("Relative rotation vector:              ", rvec_rel.T)

                # Appen to list
                translational_offset_vectors.append(t_rel.T)
                translational_rotation_vectors.append(rvec_rel.T)

    # Average translation vectors (simple mean)
    avg_translation = np.mean(translational_offset_vectors, axis=0).flatten()

    # Average rotation vectors via quaternion averaging (handles wrap-around)
    quats = np.array([
        Rotation.from_rotvec(rvec.flatten()).as_quat()
        for rvec in translational_rotation_vectors
    ])

    # Ensure quaternion sign consistency (flip if dot product with first is negative)
    for i in range(1, len(quats)):
        if np.dot(quats[0], quats[i]) < 0:
            quats[i] *= -1

    avg_quat = quats.mean(axis=0)
    avg_quat /= np.linalg.norm(avg_quat)  # Renormalize
    print("avg translation:", avg_translation)
    print("avg quaternion:", avg_quat)

    # Start slicing process with averaged pose estimation
    # On the robot we assume that we use marker 23 for

    # Convert quarternion rotation and extract rotation around z axi
    r = Rotation.from_quat(avg_quat)
    xyz = r.as_euler('xyz', degrees=True)

    file_path = slice_svg(fileName, x_offset = avg_translation[0], y_offset = avg_translation[1], rotation_offset = xyz[2])

    printer_status = "printing"

    print(f"Trying to print " + file_path)
    absPath = os.getcwd() + "/gcode/" + file_path
    
    file_name = os.path.basename(file_path)
    destination = f"0:/gcodes/{file_name}"

    # if command_connection:
    #     command_connection.connect()
    #     # Home first (Even though its in macro)
    #     res = command_connection.perform_simple_code("M98 P\"/gcodes/" + str(file_path) + "\"")
    #     print("G28 is telling us:", res)
    #     command_connection.close()

    # # Reset state
    # printer_status = "idle"

def upload_and_print(file_path: str):
    """
    Uploads a gcode file and starts printing it using only the DSF CommandConnection.
    
    :param file_path: Local path to the .gcode file to upload
    """
    printer_status = "printing"

    print(f"Trying to print " + file_path)
    absPath = os.getcwd() + "/gcode/" + file_path
    
    file_name = os.path.basename(file_path)
    destination = f"0:/gcodes/{file_name}"

    if command_connection:
        command_connection.connect()
        # Home first (Even though its in macro)
        res = command_connection.perform_simple_code("M98 P\"/gcodes/" + str(file_path) + "\"")
        print("G28 is telling us:", res)
        command_connection.close()

    # Reset state
    printer_status = "idle"

def upload_file_direct(
    local_path: str,
    remote_path: str = "gcodes/my_file.gcode",
) -> bool:
    """
    Copy a file directly into DSF's virtual SD card directory.
    Fastest option when running on the Pi itself.

    Args:
        local_path:   Path to the local file.
        remote_path:  Destination relative to the SD root,
                      e.g. "gcodes/my_job.gcode".

    Returns:
        True on success, False on failure.
    """
    dest = Path(DSF_SD_DIR) / remote_path
    dest.parent.mkdir(parents=True, exist_ok=True)

    source = Path(local_path)

    shutil.copy2(source, dest)

    return True

# From main dir, assumes that we have Chunk1.gcode stored in file dir
# python -m flaskWebServer.printBedSlicer.duet.duetAPI
if __name__ == "__main__":

    absPath = os.getcwd() + "/output/Chunk1.svg"

    upload_file_direct(absPath, "Chunk1.gcode")

    localize_slice_print(absPath, 40, 203, 1)

