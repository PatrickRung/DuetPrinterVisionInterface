import requests
import os
from dotenv import load_dotenv
import sys

from ..hardwareInterface.roborockCoordinateMoveInterface import roborockCoordinateMoveInterface

# Test run command
# python3 -m subModules.robotState.mapState
class mapState:

    def __init__(self, IP_ADDRESS, API_KEY):
        self.IP_ADDRESS_ = IP_ADDRESS
        self.API_KEY_ = API_KEY

    def getMap(self):
        # Get distance in front of roborock that it can travel
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/state/map"

        response = requests.get(url, timeout=20)

        jsonRes = response.json()

        print(jsonRes)

        return jsonRes

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

    roborockCoordMoveInter.roborockGoTo(centerCoord)

    
