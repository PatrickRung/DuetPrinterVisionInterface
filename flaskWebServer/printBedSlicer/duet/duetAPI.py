#!/usr/bin/env python3
import sys
import os
import dsf
import json
import time
import shutil

from dsf.connections import CommandConnection
from pathlib import Path

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
# python -m flaskWebServer.printBedSlicer.processSVG
if __name__ == "__main__":

    absPath = os.getcwd() + "/output/Chunk1.gcode"

    upload_file_direct(absPath, "Chunk1.gcode")

