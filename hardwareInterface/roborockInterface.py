import requests

class roborockInterface:
    
    def __init__(self, IP_ADDRESS, API_KEY):
        self.IP_ADDRESS_ = IP_ADDRESS
        self.API_KEY_ = API_KEY

    def initiateManualControl(self):
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/capabilities/ManualControlCapability"
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
        print(response.status_code)
    def disableManualControl(self):
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/capabilities/ManualControlCapability"
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
        print(response.status_code)
    def moveForward(self):
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/capabilities/ManualControlCapability"
        headers = {
            "accept": "*/*",
            "Authorization": "Basic " + self.API_KEY_ + "=",
            "Content-Type": "application/json"
        }

        payload = {
            "action": "move",
            "movementCommand": "forward"        
        }

        # Use json=payload to let requests handle JSON encoding
        response = requests.put(url, headers=headers, json=payload)
        print(response.status_code)
    def moveBackward(self):
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/capabilities/ManualControlCapability"
        headers = {
            "accept": "*/*",
            "Authorization": "Basic " + self.API_KEY_ + "=",
            "Content-Type": "application/json"
        }

        payload = {
            "action": "move",
            "movementCommand": "backward"
        }

        # Use json=payload to let requests handle JSON encoding
        response = requests.put(url, headers=headers, json=payload)
        print(response.status_code)
    def moveRotateClockwise(self):
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/capabilities/ManualControlCapability"
        headers = {
            "accept": "*/*",
            "Authorization": "Basic " + self.API_KEY_ + "=",
            "Content-Type": "application/json"
        }

        payload = {
            "action": "move",
            "movementCommand": "rotate_clockwise"
        }

        # Use json=payload to let requests handle JSON encoding
        response = requests.put(url, headers=headers, json=payload)
        print(response.status_code)
    def moveRotateCounterClockwise(self):
        url = "http://" + self.IP_ADDRESS_ + "/api/v2/robot/capabilities/ManualControlCapability"
        headers = {
            "accept": "*/*",
            "Authorization": "Basic " + self.API_KEY_ + "=",
            "Content-Type": "application/json"
        }

        payload = {
            "action": "move",
            "movementCommand": "rotate_counterclockwise"
        }

        # Use json=payload to let requests handle JSON encoding
        response = requests.put(url, headers=headers, json=payload)
        print(response.status_code)