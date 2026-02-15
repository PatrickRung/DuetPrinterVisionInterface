// Helper functions for math isolated from existing website dependencies

// Helper functions for rotation
export default function getAngularDir(initAngle: number, desiredAngle: number) : number {
    // reg case
    let regDiff = Math.abs(desiredAngle - initAngle)
    // wrappAroundCase
    let wrapDiff = Math.abs(Math.abs(360 -desiredAngle) - initAngle)

    if (regDiff > wrapDiff) {
        if (desiredAngle > initAngle) {
            return -1
        }
        else {
            return 1
        }
    }
    else {
        return (desiredAngle - initAngle) / regDiff
    }
    // Will fail unit test
    return 0
}