import requests
import time

class roborockHighResInterface:
    
    def __init__(self, IP_ADDRESS, API_KEY):
        self.IP_ADDRESS_ = IP_ADDRESS
        self.API_KEY_ = API_KEY

    def initiateHighResManualControl(self):
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/capabilities/HighResolutionManualControlCapability"
        headers = {
            "accept": "*/*",
            "Authorization": "Basic " + self.API_KEY_ + "=",
            "Content-Type": "application/json"
        }

        payload = {
            "action": "enable"
        }

        # Use json=payload to let requests handle JSON encoding
        # On turning on the script we should try to connect to the roomba and if that does not happen in 20 seconds we assume
        # roborock is not online
        response = requests.request("PUT", url, headers=headers, json=payload, timeout=20)
        if response.status_code != 200:
            print(response.status_code)
    def disableHighResManualControl(self):
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/capabilities/HighResolutionManualControlCapability"
        headers = {
            "accept": "*/*",
            "Authorization": "Basic " + self.API_KEY_ + "=",
            "Content-Type": "application/json"
        }

        payload = {
            "action": "disable"
        }

        # Use json=payload to let requests handle JSON encoding
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(response.status_code)

    def moveVectored(self, velocity, angle):
        # If the vector 
        if velocity < -1 or velocity > 1:
            print("Velocity out of bounds! velocity: " + str(velocity))
            return
        if angle < -180 or angle > 180:
            print("Angle out of bounds! angle: " + str(angle))
            return

        # Because the API rotation request do not rotate exactly to the desired rotation and are
        # off by about half, you must send the desired rotation multiplied by 2
        trueDesiredAngle = angle * 2
    
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/capabilities/HighResolutionManualControlCapability"
        headers = {
            "accept": "*/*",
            "Authorization": "Basic " + self.API_KEY_ + "=",
            "Content-Type": "application/json"
        }

        payload = {
            "action": "move",
            "vector": {
                "velocity": velocity,
                "angle": trueDesiredAngle
            }     
        }

        # Use json=payload to let requests handle JSON encoding
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(response.status_code)

        # Need delay to let movement go through otherwise the system moves on without finishing moving
        if velocity > 0:
            time.sleep(velocity * 3)
        
