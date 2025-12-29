#!/usr/bin/env python3
import sys
import cv2
import keyboard

"""
Starts a print based on the arguments passed in via the user
"""

from dsf.connections import CommandConnection


def send_simple_code():
    command_connection = CommandConnection(debug=True)
    if command_connection:
        command_connection.connect()

        try:
            # res = command_connection.set_plugin_data("ExecOnMcode", "test", "1")
            # Perform a simple command and wait for its output
            res = command_connection.perform_simple_code("M115")
            print("M115 is telling us:", res)
        finally:
            command_connection.close()


if __name__ == "__main__":

    # Establish connection to duet DSF
    send_simple_code()


    while True:

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Gracefully shutting down")
            break
