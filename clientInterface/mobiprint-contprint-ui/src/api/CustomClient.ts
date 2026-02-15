import { sendHighResolutionManualControlInteraction } from "./client";
import { Point, 
    Capability
 } from "./types"
import { floorObject } from "./utils";
import { valetudoAPI } from "./client"
import { WIDTH_CONSTANT, LENGTH_CONSTANT, OFFSET } from "../map/structures/map_structures/RobotPositionMapStructure"
import { getStructureManager, getRoborockGlobalRot } from "../map/BaseMap"
import { TextSnippet } from "@mui/icons-material";
import getAngularDir  from "./geomHelper"

// Rotates the roborock the parameter angle number of degrees
// Works by polling the state as it rotates in small increments until
// the desired angle is reached
// TODO the rotation is fairly stuttery, we could just keep on sending commands repeatedly instead of waiting for the next poll
// to send the rotate command
export async function roborockRotate(angle: number) {
    console.log("Starting 90 degree rotation");
    
    const ROBOT_STATE_URL = '/api/v2/robot/state';

    if (angle > 360 || angle < 0) {
        console.error("Angle to rotate to must be between !")
        return
    }
    
    try {

        // We can trust this angle because most likely roborock will have learned room already due to previous
        // go to command
        const initialAngle = getRoborockGlobalRot()

        let targetAngle = angle;        // Leaving this in case wee want to do more pre processing
        let angularVel = getAngularDir(initialAngle, targetAngle)

        // Which dir roborock rotate
        console.log(`Initial angle: ${initialAngle}, Target angle: ${targetAngle}`);
        
        // Import the API client function
        
        
        // Start rotation - enable manual control and start rotating
        await sendHighResolutionManualControlInteraction({
            action: "enable"
        });
        
        // Give it a moment to enable
        await new Promise(resolve => setTimeout(resolve, 300));
        
        let rotationComplete = false;
        let pollCount = 0;
        const MAX_POLLS = 100; // Safety limit (50 seconds max at 500ms intervals)
        
        // Poll until rotation is complete
        while (!rotationComplete && pollCount < MAX_POLLS) {
            await new Promise(resolve => setTimeout(resolve, 500)); // Wait 500ms between polls
            
            const currentStateResponse = await fetch(ROBOT_STATE_URL);
            const currentState = await currentStateResponse.json();
            const currentAngle = getRoborockGlobalRot();
            
            // Calculate angle difference (accounting for 360 degree wraparound)
            let angleDiff = Math.abs(targetAngle - currentAngle);
            if (angleDiff > 180) {
                angleDiff = 360 - angleDiff;
            }
            
            console.log(`Current angle: ${currentAngle}, Diff from target: ${angleDiff}`);
            
            // Check if we're within 2 degrees of target (tolerance for sensor accuracy)
            if (angleDiff < 5) {
                rotationComplete = true;
                console.log("Rotation complete!");
                break;
            }

            if (!rotationComplete) {
                console.error("Rotation timeout - max polls reached");
                // Attempt to stop rotation anyway
                await sendHighResolutionManualControlInteraction({
                    action: "move",
                    vector: {
                        velocity: 0,
                        angle: 20 * angularVel
                    }
                });
            }
            
            pollCount++;
        }
        
    } catch (error) {
        console.error("Error during rotation:", error);
        // Try again
        setTimeout(() => {
            roborockRotate(angle);
        }, 3000)

    }
}

