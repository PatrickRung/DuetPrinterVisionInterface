import requests
import os
from dotenv import load_dotenv
import sys
import numpy
import time

from ..hardwareInterface.roborockCoordinateMoveInterface import roborockCoordinateMoveInterface

# Test run command
# python3 -m subModules.robotState.mapState
class mapState:

    def __init__(self, IP_ADDRESS, API_KEY):
        self.IP_ADDRESS_ = IP_ADDRESS
        self.API_KEY_ = API_KEY
        self.mapData_ = None

    def getMap(self):
        # Get distance in front of roborock that it can travel
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/state/map"

        response = requests.get(url, timeout=20)

        jsonRes = response.json()

        print(jsonRes)

        self.mapData_ = jsonRes

        return jsonRes
    
    def build_obstacle_set(self):

        if (self.mapData_ == None):
            print("map data not generated yet, run getMap() to fetch new map data")
            return

        obstacles = set()

        for layer in self.mapData_["layers"]:
            if layer["type"] not in ("wall", "segment"):
                continue

            data = layer["compressedPixels"]
            i = 0
            while i < len(data):
                x, y, count = data[i:i+3]
                for dx in range(count):
                    obstacles.add((x + dx, y))
                i += 3
        return obstacles
    
    def get_robot_pose(self):
        for entity in self.mapData_["entities"]:
            if entity["type"] == "robot_position":
                x, y = entity["points"]
                angle = entity["metaData"]["angle"]
                return x, y, angle
        raise ValueError("Robot position not found")

if __name__ == "__main__":  
    # Loads the dotenv
    load_dotenv()

    # Roborock API key so that git stops complaining
    api_key = str(os.getenv("API_KEY"))
    IP_ADDRESS = str(os.getenv("IP_ADDRESS"))
    print("Address: " + IP_ADDRESS)

    roborockMapStateRef = mapState(IP_ADDRESS=IP_ADDRESS, 
                                   API_KEY=api_key)

    roborockCoordMoveInter = roborockCoordinateMoveInterface(IP_ADDRESS=IP_ADDRESS, 
                                                             API_KEY=api_key)

    mapRes = roborockMapStateRef.getMap()

    # Get size of map
    width = mapRes["size"]["x"]
    height = mapRes["size"]["y"]

    # Get center of map
    centerCoord = [width / 2, height / 2]

    # roborockCoordMoveInter.roborockGoTo(centerCoord)

    # based on obstace go to farthest dir

    # Go to self to calibrate to new pos
    mapRes = roborockMapStateRef.getMap()
    rx, ry, angle = roborockMapStateRef.get_robot_pose()

    roborockCoordMoveInter.roborockGoTo((rx + 20, ry))

    max_distance = 200

    
    obstacles = roborockMapStateRef.build_obstacle_set()

    print(angle)
    # Test go as far forward as possible
    rad = numpy.radians(270)
    step_x = numpy.cos(rad)
    step_y = numpy.sin(rad)

    x, y = float(rx), float(ry)
    steps = 0

    while True:
        x += 1
        ix, iy = int(round(x)), int(round(y))

        # Stop at map edge
        if ix < 0 or iy < 0 or ix >= width or iy >= height:
            break

        # Stop at obstacle
        if (ix, iy) in obstacles:
            break

        steps += 1
        if max_distance and steps >= max_distance:
            break
    print("X: " + str(ix) + " Y: " + str(iy))

    destCoordTuple = (ix, iy)

    
    


    
