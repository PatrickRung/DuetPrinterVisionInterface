# Setup script that installs all required dependencies

python -m pip install keyboard
python -m pip install requests
python -m pip install python-dotenv
python -m pip install opencv-contrib-python         # Required to be opencv-contrib due to use pose estimation
python -m pip install scipy                         # For matrix calculations
python -m pip install flask-cors
python -m pip install svg.path
python -m pip install matplotlib
python -m pip install PyQt6                                   # Bug fix for matplot lib displaying
python -m pip install flask-cors
python -m pip install dsf-python
python -m pip install picamera2

