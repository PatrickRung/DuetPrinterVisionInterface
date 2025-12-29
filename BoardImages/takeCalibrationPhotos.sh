# Might need to run:
# chmod 700 takeCalibrationPhotos.sh
# to get the calibration image script to run due to permission issues
for i in {1..11}
do
	libcamera-still -q 80 -o image$i.jpg --width 640 --height 480
done