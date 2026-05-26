import { sendHighResolutionManualControlInteraction } from "./client";
import { valetudoAPI } from "./client"
import { getStructureManager, getRoborockGlobalRot } from "../map/BaseMap"
import { getAngularDir } from "./geomHelper"

// PID gains — tune these for your robot's inertia and poll rate
const PID_KP = 0.7;   // Proportional: main driving force
const PID_KI = 0.01;  // Integral: corrects steady-state offset
const PID_KD = 0.4;   // Derivative: damps oscillation / overshoot
const INTEGRAL_CLAMP = 50; // Prevents integral windup
const ANGLE_TOLERANCE = 5; // Degrees within which we consider rotation done
const POLL_INTERVAL_MS = 500;
const MAX_POLLS = 100;
const MAX_VELOCITY = 25; // Upper bound for the velocity command
const MIN_VELOCITY = 8;  // Lower bound so the robot actually moves

// Returns the shortest signed angular difference in [-180, 180]
function shortestAngularDiff(from: number, to: number): number {
    let diff = to - from;
    while (diff > 180)  diff -= 360;
    while (diff < -180) diff += 360;
    return diff;
}

export async function roborockRotate(angle: number, cb?: () => void) {
    console.log(`roborockRotate: target=${angle}°`);

    if (angle > 360 || angle < 0) {
        console.error("Angle must be in [0, 360]. Received: " + angle);
        return;
    }

    try {
        const ROBOT_STATE_URL = '/roborock/api/v2/robot/state';

        await sendHighResolutionManualControlInteraction({ action: "enable" });
        await new Promise(resolve => setTimeout(resolve, 300));

        // PID state
        let integral = 0;
        let prevError = shortestAngularDiff(getRoborockGlobalRot(), angle);
        let pollCount = 0;
        let rotationComplete = false;

        while (!rotationComplete && pollCount < MAX_POLLS) {
            await new Promise(resolve => setTimeout(resolve, POLL_INTERVAL_MS));

            await fetch(ROBOT_STATE_URL); // trigger a state refresh
            const currentAngle = getRoborockGlobalRot();

            // Signed error: positive = need to rotate CCW, negative = CW
            const error = shortestAngularDiff(currentAngle, angle);
            const absError = Math.abs(error);

            console.log(`Poll ${pollCount}: current=${currentAngle}° error=${error.toFixed(1)}°`);

            if (absError < ANGLE_TOLERANCE) {
                rotationComplete = true;
                console.log("Rotation complete!");
                await sendHighResolutionManualControlInteraction({ action: "disable" });
                cb?.();
                break;
            }

            // PID computation
            const dt = POLL_INTERVAL_MS / 1000; // seconds
            const derivative = (error - prevError) / dt;
            integral = Math.max(-INTEGRAL_CLAMP,
                        Math.min(INTEGRAL_CLAMP, integral + error * dt));

            const rawOutput = PID_KP * error
                            + PID_KI * integral
                            + PID_KD * derivative;

            // Clamp to [MIN_VELOCITY, MAX_VELOCITY] preserving sign
            const sign = rawOutput >= 0 ? 1 : -1;
            const clampedVelocity = sign * Math.max(MIN_VELOCITY,
                                            Math.min(MAX_VELOCITY, Math.abs(rawOutput)));

            console.log(`PID: e=${error.toFixed(1)} i=${integral.toFixed(1)} d=${derivative.toFixed(1)} → vel=${clampedVelocity.toFixed(1)}`);

            await sendHighResolutionManualControlInteraction({
                action: "move",
                vector: {
                    velocity: 0,
                    angle: clampedVelocity  // positive = one dir, negative = other
                }
            });

            prevError = error;
            pollCount++;
        }

        if (!rotationComplete) {
            console.error("Rotation timeout after max polls");
            await sendHighResolutionManualControlInteraction({ action: "disable" });
        }

    } catch (error) {
        console.error("Error during rotation:", error);
        setTimeout(() => roborockRotate(angle, cb), 3000);
    }
}