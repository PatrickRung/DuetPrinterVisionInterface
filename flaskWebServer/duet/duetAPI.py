#!/usr/bin/env python3
import sys
import os
import dsf
import json
import time
print(dsf.__file__)
from dsf.connections import CommandConnection

# Try to create upon creation of program (Timeout really big so we know when print done)
command_connection = CommandConnection(debug=True, timeout=1000000)

if command_connection:
    command_connection.connect()

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
def get_print_status():
    return printer_status

def upload_and_print(file_path: str):
    """
    Uploads a gcode file and starts printing it using only the DSF CommandConnection.
    
    :param file_path: Local path to the .gcode file to upload
    """
    printer_status = "printing"

    print(f"Trying to print")
    absPath = os.getcwd() + "/gcode/" + file_path
    
    file_name = os.path.basename(file_path)
    destination = f"0:/gcodes/{file_name}"

    if command_connection:
        command_connection.connect()
        # Home first (Even though its in macro)
        res = command_connection.perform_simple_code("M98 P\"/macros/prusa_mini_bed_sweep.gcode\"")
        print("G28 is telling us:", res)
        command_connection.close()

    # Reset state
    printer_status = "idle"

if __name__ == "__main__":

    # Establish connection to duet DSF
    send_simple_code()


    while True:

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Gracefully shutting down")
            break
