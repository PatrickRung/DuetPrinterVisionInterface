# MobiPrint large scale printing codebase

# Raspberry PI backend (3D printer and CV base movement controller)
Below are instructions for the python backend running on the raspberry pi providng computer vision based localization

You will need to set up the virtual environment using the system site package, thus use this command.
This is important for getting the Python camera to work with the virtual environment.

python3 -m venv --system-site-packages env

Then you want to source the virtual environment and download the following dependencies:
source myenv/bin/activate
- python -m pip install keyboard
- python -m pip install requests
- python -m pip install python-dotenv
- python -m pip install opencv-contrib-python         # Required to be opencv-contrib due to use of pose estimation
- python -m pip install scipy                         # For matrix calculations
- python -m pip install flask flask-restful           # For python webserver to handle Raspberry PI API calls (Yes the architcture is kind of crazy right now)
- python -m pip install svg.path                      # For SVG line parsing
- pip install matplotlib                              # For debugging SVG line placement
- pip install PyQt6                                   # Bug fix for matplot lib displaying

If dependency issues still arise, you might need to install the following packages.
python3 -m pip install picamera2

Before running anything, make sure that the env file is filled out.
NOTHING WORKS IF THE .env FILE IS INCORRECT
Contents are to be formated as shown below:
API_KEY=Roborock API Key
IP_ADDRESS=Roborock IP Address

After installing the necessary libraries and setting up the .env file, you will need to calibrate the camera.
This is required to get pose estimation to work properly. This repo already contains a .yaml file containing the
Calibration for the Raspberry pi 5 official camera; however, if you are to use your own, you will need to calibrate it.
The bash file in the BoardImages folder will allow you to take 11 photos of the Aruco board for calibration and more.
Instructions can be found here https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html and on the bash file

If all dependencies are met, run:
sudo env/bin/python3 controlRoborock.py 

possible flags:
    '-d'       Prevents any API calls from being sent to the Roborock. Useful for testing a computer vision algorithm without waiting for Roborock responses
Note to self, the keyboard library does not work with VNC viewer. You must use an external keyboard.
Once the program is launched for manual control, the 2 key is to turn on, and the 4 key is to turn. 

Common issues:
For the run script, runRoborockControlScript.sh if it does not work, run the command to give it permissions:
chmod 700 runRobrockControlScript.sh 

If there is an error about incompatible data formatting between simplejpeg and numpy, you might need to go and reinstall simplejpeg:
1. sudo apt remove python3-simplejpeg OR python3 -m pip uninstall simplejpeg # (Depending on where it is installed)
2. python -m pip install --no-cache-dir simplejpeg # Reinstall
3. python3 -m pip install picamera2 # need to reinstall camera

# React frontend (Slicer, visual debug tool and first pass controller)
Below are details for the client frontend

The formal read me for the client front end is located at /DuetPrinterVisionInterface/clientInterface/README.md
The front end is designed to be a debugging tool as well as provide the first layer print jobs that will print the first set
of ArUco markers.
