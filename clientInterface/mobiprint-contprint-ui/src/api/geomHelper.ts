// Helper functions for math isolated from existing website dependencies

// Helper functions for rotation
export function getAngularDir(initAngle: number, desiredAngle: number): number {
    // Normalize the raw difference into (-180, 180]
    let diff = ((desiredAngle - initAngle) + 360) % 360;
    if (diff > 180) diff -= 360;

    // Positive diff → counterclockwise (+1), negative → clockwise (-1)
    // Adjust sign convention to match your robot's rotation direction
    return diff > 0 ? 1 : -1;
}

// Vector to roborock rotation (0 degrees is to the left, 90 degrees is to the right)
export function getRobotAngleFromVector(vector: DOMPoint) : number {

    // Consider 4 quadrant cases
    // Q1
    if (vector.x >= 0 && vector.y >= 0) {
        return Math.abs(Math.atan(vector.y / vector.x) * (180 / Math.PI)) + 180
    }
    // Q2
    else if (vector.x < 0 && vector.y > 0) {
        return Math.atan(vector.y / vector.x) * (180 / Math.PI) + 360
    }
    // Q3
    else if (vector.x < 0 && vector.y <= 0) {
        return Math.abs(((Math.atan(vector.y / vector.x) * (180 / Math.PI))));
    }
    // Q4
    else if (vector.x >= 0 && vector.y < 0) {
        return 180 + (Math.atan(vector.y / vector.x) * (180 / Math.PI))
    }
    return 0;
}
