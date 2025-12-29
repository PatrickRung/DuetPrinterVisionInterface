import requests
import time

import os
import sys
from dotenv import load_dotenv
import numpy

import hardwareInterface.roborockHighResInterface as roborockHighResInterface


class roborockCoordinateMoveInterface:
    
    def __init__(self, IP_ADDRESS, API_KEY):
        self.IP_ADDRESS_ = IP_ADDRESS
        self.API_KEY_ = API_KEY
        self.roborockHighResInterfaceReference = roborockHighResInterface.roborockHighResInterface(IP_ADDRESS=IP_ADDRESS, 
                                                                                                   API_KEY=api_key)

    # returns two variables being the coordinate of the position represented by two integers that are in CM
    # and the rotation in degrees
    def getRoborockPos(self):
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/state/map"

        response = requests.get(url, timeout=20)

        jsonRes = response.json()

        # Dictionary entry for position is located in the entities attribute of the json response
        # The index for the position is the 3rd entry
        # Points are represented in CM
        

        coordinateOfPos = jsonRes["entities"][2]['points']
        print(coordinateOfPos)
        rotationOfPos = jsonRes["entities"][2]['metaData']['angle']
        print(rotationOfPos)

        if response.status_code != 200:
            print(response.status_code)
        
        return coordinateOfPos, rotationOfPos

    def checkEvents(self):
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/events"

        response = requests.get(url, timeout=20)
        print(response.json)
        print(response.content)
        if response.status_code != 200:
            print(response.status_code)

    # Distance is the length of the desired distance for the roborock to travel forward in CM
    def moveLidarBased(self, desiredDistance):
        initPos, rot = self.getRoborockPos()
        print("Starting pos " + str(initPos))

        self.roborockHighResInterfaceReference.initiateHighResManualControl()

        distanceFromStart = 0

        while distanceFromStart < desiredDistance:
            self.roborockHighResInterfaceReference.moveVectored(0.03, 0)
            currPos, rot = roborockCoordMoveInter.getRoborockPos()
            newDistanceFromStart = numpy.sqrt(numpy.power(numpy.abs(currPos[0] - initPos[0]), 2) + numpy.power(numpy.abs(currPos[1] - initPos[1]), 2))

            # Previously holding a reference to the old distance was used to remove any spikes that were occuring as they were causing the move to location
            distanceFromStart = newDistanceFromStart
            
            print(distanceFromStart)

    # Distance is the length of the desired distance for the roborock to travel forward in CM
    # note to self on 12/29/2025
    # This method is very hard to use as the initial rotation is hard to get and update, the accuracy for the distance is also frequently
    # offset by the state not updating making this method a little confusing to use, might be better to just move slow in the end. Also 
    # cannot adjust speed
    def moveUsingGoTo(self, desiredDistance):
        initPos, rot = self.getRoborockPos()

        newPosX = initPos[0] + (desiredDistance * numpy.cos(numpy.deg2rad(rot)))
        newPosY = initPos[1] + (desiredDistance * numpy.sin(numpy.deg2rad(rot)))
        
        tupleCoord = (int(newPosX), int(newPosY))
        print(tupleCoord)

        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/capabilities/GoToLocationCapability"
        headers = {
            "accept": "*/*",
            "Authorization": "Basic " + self.API_KEY_ + "=",
            "Content-Type": "application/json"
        }

        payload = {
            "action": "goto",
            "name": "string",
            "coordinates": {
                "x": tupleCoord[0],
                "y": tupleCoord[1]
            },
            "id": "string",
            "metaData": {}  
        }

        # Use json=payload to let requests handle JSON encoding
        response = requests.put(url, headers=headers, json=payload)
        print(response)
        print(response.content)

    # Distance is the length of the desired distance for the roborock to travel forward in CM
    def moveLidarBased(self, desiredDistance):
        initPos, rot = self.getRoborockPos()
        print("Starting pos " + str(initPos))

        self.roborockHighResInterfaceReference.initiateHighResManualControl()

        distanceFromStart = 0

        while distanceFromStart < desiredDistance:
            self.roborockHighResInterfaceReference.moveVectored(0.03, 0)
            currPos, rot = roborockCoordMoveInter.getRoborockPos()
            newDistanceFromStart = numpy.sqrt(numpy.power(numpy.abs(currPos[0] - initPos[0]), 2) + numpy.power(numpy.abs(currPos[1] - initPos[1]), 2))

            # Previously holding a reference to the old distance was used to remove any spikes that were occuring as they were causing the move to location
            distanceFromStart = newDistanceFromStart
            
            print(distanceFromStart)
        
# main for testing the methods in this class
if __name__ == "__main__":  
    # Loads the dotenv
    load_dotenv()

    # Roborock API key so that git stops complaining
    api_key = str(os.getenv("API_KEY"))
    IP_ADDRESS = str(os.getenv("IP_ADDRESS"))
    print("Address: " + IP_ADDRESS)

    roborockCoordMoveInter = roborockCoordinateMoveInterface(IP_ADDRESS=IP_ADDRESS, 
                                                             API_KEY=api_key)

    roborockCoordMoveInter.moveLidarBased(20)





    