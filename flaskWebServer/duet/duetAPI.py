#!/usr/bin/env python3
import sys
import os
from dsf.connections import CommandConnection

# Try to create upon creation of program
command_connection = CommandConnection(debug=True)

def send_simple_code():
    
    if command_connection:
        command_connection.connect()

        try:
            # res = command_connection.set_plugin_data("ExecOnMcode", "test", "1")
            # Perform a simple command and wait for its output
            res = command_connection.perform_simple_code("M115")
            print("M115 is telling us:", res)
        finally:
            command_connection.close()

def upload_and_print(file_path: str):
    """
    Uploads a gcode file and starts printing it using only the DSF CommandConnection.
    
    :param file_path: Local path to the .gcode file to upload
    """
    import os

    print(f"Trying to print")
    absPath = os.getcwd() + "/gcode/" + file_path

    if not os.path.exists(absPath):
        print(f"Error: File '{absPath}' not found by os searcher.")
        return

    
    file_name = os.path.basename(file_path)
    destination = f"0:/gcodes/{file_name}"

    if command_connection:
        command_connection.connect()

        try:
            # Upload the file to the Duet SD card
            command_connection.perform_simple_code

        finally:
            command_connection.close()

if __name__ == "__main__":

    # Establish connection to duet DSF
    send_simple_code()


    while True:

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Gracefully shutting down")
            break
