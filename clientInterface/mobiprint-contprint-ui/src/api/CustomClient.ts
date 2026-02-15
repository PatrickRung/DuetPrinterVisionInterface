import { sendHighResolutionManualControlInteraction } from "./client";
import { Point, 
    Capability
 } from "./types"
import { floorObject } from "./utils";
import { valetudoAPI } from "./client"
import { WIDTH_CONSTANT, LENGTH_CONSTANT, OFFSET } from "../map/structures/map_structures/RobotPositionMapStructure"
import { getStructureManager } from "../map/BaseMap"

// Helper function to extract angle from state JSON
const getAngleFromState = (state: any): number => {
    const robotPosition = state.map?.entities?.find((entity: any) => entity.type === 'robot_position');
    console.log(robotPosition.metaData.angle)
    return robotPosition.metaData.angle; // Third element is the angle
};


// Rotates the roborock the parameter angle number of degrees
// Works by polling the state as it rotates in small increments until
// the desired angle is reached
// TODO the rotation is fairly stuttery, we could just keep on sending commands repeatedly instead of waiting for the next poll
// to send the rotate command
export async function roborockRotate(angle: number) {
    console.log("Starting 90 degree rotation");
    
    const ROBOT_STATE_URL = '/api/v2/robot/state';
    
    try {
        // Get initial angle
        const initialStateResponse = await fetch(ROBOT_STATE_URL);
        const initialState = await initialStateResponse.json();
        const initialAngle = getAngleFromState(initialState);
        const targetAngle = (initialAngle + angle) % 360;
        
        console.log(`Initial angle: ${initialAngle}, Target angle: ${targetAngle}`);
        
        // Import the API client function
        
        
        // Start rotation - enable manual control and start rotating
        await sendHighResolutionManualControlInteraction({
            action: "enable"
        });
        
        // Give it a moment to enable
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Start rotation
        await sendHighResolutionManualControlInteraction({
            action: "move",
            vector: {
                velocity: 0,
                angle: 10
            }
        });
        
        let rotationComplete = false;
        let pollCount = 0;
        const MAX_POLLS = 100; // Safety limit (50 seconds max at 500ms intervals)
        
        // Poll until rotation is complete
        while (!rotationComplete && pollCount < MAX_POLLS) {
            await new Promise(resolve => setTimeout(resolve, 500)); // Wait 500ms between polls
            
            const currentStateResponse = await fetch(ROBOT_STATE_URL);
            const currentState = await currentStateResponse.json();
            const currentAngle = getAngleFromState(currentState);
            
            // Calculate angle difference (accounting for 360 degree wraparound)
            let angleDiff = Math.abs(targetAngle - currentAngle);
            if (angleDiff > 180) {
                angleDiff = 360 - angleDiff;
            }
            
            console.log(`Current angle: ${currentAngle}, Diff from target: ${angleDiff}`);
            
            // Check if we're within 2 degrees of target (tolerance for sensor accuracy)
            if (angleDiff < 2) {
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
                        angle: 10
                    }
                });
            }
            
            pollCount++;
        }
        
    } catch (error) {
        console.error("Error during rotation:", error);
        // Try to disable manual control in case of error
        try {
            await sendHighResolutionManualControlInteraction({
                action: "disable"
            });
        } catch (cleanupError) {
            console.error("Error during cleanup:", cleanupError);
        }
    }
}