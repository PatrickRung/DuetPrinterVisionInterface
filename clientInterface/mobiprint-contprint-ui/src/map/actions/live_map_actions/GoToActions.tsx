import {
    useGoToMutation,
    useRobotStatusQuery
} from "../../../api";
import React from "react";
import {CircularProgress, Grid2, Typography} from "@mui/material";
import {ActionButton} from "../../Styled";
import GoToTargetClientStructure from "../../structures/client_structures/GoToTargetClientStructure";
import IntegrationHelpDialog from "../../../components/IntegrationHelpDialog";
import StructureManager from "./../../StructureManager";
import {useLongPress} from "use-long-press";
import {floorObject} from "../../../api/utils";
import {PointCoordinates} from "../../utils/types";
import {
    Clear as ClearIcon,
    PlayArrow as GoIcon
} from "@mui/icons-material";
import {sendGoToCommand} from "../../../api/client"
import { getRoborockGlobalPos, getStructureManager } from "../../BaseMap"

interface GoToActionsProperties {
    goToTarget: GoToTargetClientStructure | undefined;

    convertPixelCoordinatesToCMSpace(coordinates: PointCoordinates) : PointCoordinates

    onClear(): void;
}

// Path traverse state machine
const RobotGoToStates = Object.freeze({
    INIT: "Initalized",
    TRAVERSING: "Traversing",
    FIN: "Finished",
    NODEST: "No destination"
});

class MultiPointGoToState {

    // Properties
    destinationsForRoborock : GoToTargetClientStructure[];
    currDestination : GoToTargetClientStructure | undefined;
    prevPoint: number[] | null;
    structureManagerRef: StructureManager | null;
    existingTimer: boolean;                                 // Denotes whether or not there is a timer active 
                                                            // !! DO NOT CREATED MULTIPLE TIMERS CHECK THIS VAR
    withinDesiredAreaCount: number;
    hardCoded: boolean;
    // Can be any of the robot states
    currentTraverseState: typeof RobotGoToStates.INIT |
                          typeof RobotGoToStates.TRAVERSING |
                          typeof RobotGoToStates.FIN |
                          typeof RobotGoToStates.NODEST;

    constructor() {
        this.prevPoint = null;
        this.currDestination = undefined;
        this.structureManagerRef = getStructureManager();
        this.existingTimer = false;
        this.withinDesiredAreaCount = 0;
        this.hardCoded = true;
        this.currentTraverseState = RobotGoToStates.NODEST;
        if (this.hardCoded) {
            // Circle pattern
            // this.destinationsForRoborock = [new GoToTargetClientStructure(519, 507),
            //                                 new GoToTargetClientStructure(507, 503),
            //                                 new GoToTargetClientStructure(505, 509),
            //                                 new GoToTargetClientStructure(507, 516)];
            // Real circle pattern
            this.destinationsForRoborock = [new GoToTargetClientStructure(521.04, 509.517),
                                            new GoToTargetClientStructure(516.868, 500.782),
                                            new GoToTargetClientStructure(510.089, 500),
                                            new GoToTargetClientStructure(505, 503),
                                            new GoToTargetClientStructure(503, 507),
                                            new GoToTargetClientStructure(509, 512),
                                            new GoToTargetClientStructure(518, 513),
                                            new GoToTargetClientStructure(521, 510)];
        }
        else {
            this.destinationsForRoborock = [];
        }
    }

    // Run this every 5 seconds and if not go to command is received, that signifies that 
    // the go to command has received a response
    // Loop ends when withinDesiredAreaCount achieves 3 polls
    goToCommandHeartbeatCheck() {
        if (this.structureManagerRef == null || this.currDestination == null) {
            console.log("Structure manager not loaded")
            return;
        }

        let currPoint = getRoborockGlobalPos();

        if (this.prevPoint == null) {
            this.prevPoint = currPoint;
        }
        // Check if we stayed in the same spot for more than 1 iteration, then reset go to state
        else if (checkAproxEquals(currPoint[0], this.prevPoint[0], 0.01) && 
                checkAproxEquals(currPoint[1], this.prevPoint[1], 0.01)) {

            // If the position is the same, we could be stuck or at the start so code in this scoped
            // handles that case
            let currPointInPixelSpace = this.structureManagerRef.convertCMCoordinatesToPixelSpace({x: currPoint[0], y: currPoint[1]});
            console.log("Stationary at " + getRoborockGlobalPos() + 
                "In non CM space" + currPointInPixelSpace.x + ", " + currPointInPixelSpace.y + ": TIMESTAMP: " + Date.now())

            let pointsCM = this.structureManagerRef.convertPixelCoordinatesToCMSpace({x: this.currDestination.x0, y: this.currDestination.x0});
            console.log("Desired "  + pointsCM.x + " " + pointsCM.y)

            // Check if we reached destination (We accept anywhere within 100 CM range)
            let magDiff = Math.pow(Math.pow(currPoint[0] - pointsCM.x, 2) + Math.pow(currPoint[1] - pointsCM.y, 2), 0.5)

            // NOTE the mag diff threshold is to be changed in the event that the roborock never reaches or acknowledges
            // that is has reached the destination
            if (this.currDestination != undefined && magDiff < 50) {

                // Update state
                this.withinDesiredAreaCount++;

                // Needs to stay at end poll for 3 loops
                if (this.withinDesiredAreaCount >= 3) {
                    this.existingTimer = false;
                    this.prevPoint = null;
                    this.currDestination = undefined;

                    // Trigger next go to!
                    console.log("fin execution")
                    this.executeConsecGoTo()
                    return;
                }
            }
            else {
                console.log("Did not make it")
                this.withinDesiredAreaCount = 0;
            }
        }

        // Update prevPoint
        this.prevPoint = currPoint;

        setTimeout(() => {
            this.goToCommandHeartbeatCheck()
        }, 3000)
    }

    initiateGoToCommandChecker() {
        if (!this.existingTimer) {
            this.goToCommandHeartbeatCheck()
            this.existingTimer = true;
        }
    }

    clearDestinationState() {
        if (this.destinationsForRoborock != null) {
            this.destinationsForRoborock.length = 0
        }
    }

    updateDestinations(goToTarget : GoToTargetClientStructure) {

        if (this.hardCoded) {
            console.error("The path is designated as hard coded! Cannot add points, tried to add point" + goToTarget.x0 + ", " + goToTarget.y0)
            return;
        }

        let destContainsCoord = false;
        for (let i = 0; i < this.destinationsForRoborock.length && !destContainsCoord; i++) {
            var currCoord = this.destinationsForRoborock[i];
            if (typeof goToTarget !== "undefined" && 
                checkAproxEquals(goToTarget.x0, currCoord.x0, 0.01) && 
                checkAproxEquals(goToTarget.y0, currCoord.y0, 0.01)) {
                    destContainsCoord = true;
            }
        }

        if (!destContainsCoord && typeof goToTarget !== "undefined") {
            console.log("Add " + goToTarget.x0 + ", " + goToTarget.y0)
            this.destinationsForRoborock.push(goToTarget);
        }
    }

    executeConsecGoTo() {
        console.log(this.destinationsForRoborock.length)
        if (this.destinationsForRoborock.length == 0) {
            return;
        }

        let recentGoTo = this.destinationsForRoborock.shift() 

        // Refetch structure manager
        this.structureManagerRef = getStructureManager();
        if (recentGoTo == undefined || 
            this.structureManagerRef == null) {
                console.error("Tried to go to multiple with either existing path or unable to fetch required objects")
                return;
        }

        this.currDestination = recentGoTo;
        let CMCoords = this.structureManagerRef.convertPixelCoordinatesToCMSpace({x: recentGoTo.x0, y: recentGoTo.y0})
        console.log("start")
        sendGoToCommand(CMCoords);
        // Sending the go to command right away leads to issues, delay for 3 seconds
        setTimeout(() => {
            sendGoToCommand(CMCoords);
        }, 3000)
        // this.withinDesiredAreaCount = 0;
        this.currentTraverseState = RobotGoToStates.INIT;
        // this.initiateGoToCommandChecker()
    }

    updateTraverseFSM(newStatus: 
        "moving" | "paused" | "error" | "docked" | "idle" | "returning" | "cleaning" | "manual_control" | undefined
    ) {
        // Check current state
        if (this.currentTraverseState === RobotGoToStates.NODEST) {
            // Don't do anything, wait for a destination
        }
        else if (this.currentTraverseState === RobotGoToStates.INIT)  {
            if (newStatus === "moving") {
                console.log("start moving")
                this.currentTraverseState = RobotGoToStates.TRAVERSING;
            }
        }
        else if (this.currentTraverseState === RobotGoToStates.TRAVERSING) {
            if (newStatus === "paused" || newStatus === "idle") {
                this.currentTraverseState = RobotGoToStates.NODEST;
                console.log("finished moving")

                // Will handle if there is any more go to commands or if its empty
                this.executeConsecGoTo()
            }
        }
    }
}

var multiPointGoToRef = new MultiPointGoToState() 

function checkAproxEquals(val1: number, val2: number, thresh: number) {
    var diff = Math.abs(val1 - val2);
    return diff < thresh;
}

export function clearDestinations() {
    multiPointGoToRef.clearDestinationState();
}


const GoToActions = (
    props: GoToActionsProperties
): React.ReactElement => {
    // Create list for target points:

    const {goToTarget, convertPixelCoordinatesToCMSpace, onClear} = props;
    const [integrationHelpDialogOpen, setIntegrationHelpDialogOpen] = React.useState(false);
    const [integrationHelpDialogPayload, setIntegrationHelpDialogPayload] = React.useState("");

    // Verify coordinate is not already in destinationsForRoborock
    // Only update destinations when goToTarget actually changes
    // How this works is that it checks whether goToTarget?.x0, goToTarget?.y0 have changed
    // If so it will then re run this code. Otherwise react will call this code every time it renders
    // which is frequent thus keeping the list populated
    React.useEffect(() => {
        if (goToTarget !== undefined) {
            multiPointGoToRef.updateDestinations(goToTarget);
        }
    }, [goToTarget?.x0, goToTarget?.y0]); // Only run when coordinates change

    const {data: status} = useRobotStatusQuery((state) => {
        return state.value;
    });
    const {
        mutate: goTo,
        isPending: goToIsExecuting
    } = useGoToMutation({
        onSuccess: onClear,
    });

    const canGo = status === "idle" || status === "docked" || status === "paused" || status === "returning" || status === "error";

    // Update go to FSM
    multiPointGoToRef.updateTraverseFSM(status);

    const handleClick = React.useCallback(() => {
        if (!canGo || !goToTarget) {
            return;
        }
        console.log("init multi go to")
        multiPointGoToRef.executeConsecGoTo()
    }, [canGo, goToTarget, goTo, convertPixelCoordinatesToCMSpace]);

    const handleLongClick = React.useCallback(() => {
        if (!goToTarget) {
            return;
        }

        setIntegrationHelpDialogPayload(JSON.stringify({
            action: "goto",
            coordinates: floorObject(convertPixelCoordinatesToCMSpace({x: goToTarget.x0, y: goToTarget.y0})),
        }, null, 2));

        setIntegrationHelpDialogOpen(true);
    }, [goToTarget, convertPixelCoordinatesToCMSpace]);

    const setupClickHandlers = useLongPress(
        handleLongClick,
        {
            onCancel: (event) => {
                handleClick();
            },
            threshold: 500,
            captureEvent: true,
            cancelOnMovement: true,
        }
    );


    return (
        <>
            <Grid2 container spacing={1} direction="row-reverse" flexWrap="wrap-reverse">
                <Grid2>
                    <ActionButton
                        disabled={goToIsExecuting || !canGo || !goToTarget}
                        color="inherit"
                        size="medium"
                        variant="extended"
                        {...setupClickHandlers()}
                    >
                        <GoIcon style={{marginRight: "0.25rem", marginLeft: "-0.25rem"}}/>
                        Go To Location
                        {goToIsExecuting && (
                            <CircularProgress
                                color="inherit"
                                size={18}
                                style={{marginLeft: 10}}
                            />
                        )}
                    </ActionButton>
                </Grid2>
                <Grid2>
                    {
                        goToTarget &&
                        <ActionButton
                            color="inherit"
                            size="medium"
                            variant="extended"
                            onClick={onClear}
                        >
                            <ClearIcon style={{marginRight: "0.25rem", marginLeft: "-0.25rem"}}/>
                            Clear
                        </ActionButton>
                    }
                </Grid2>
                {
                    !canGo &&
                    <Grid2>
                        <Typography variant="caption" color="textSecondary">
                            Cannot go to point while the robot is busy
                        </Typography>
                    </Grid2>
                }
            </Grid2>
            <IntegrationHelpDialog
                dialogOpen={integrationHelpDialogOpen}
                setDialogOpen={(open: boolean) => {
                    setIntegrationHelpDialogOpen(open);
                }}
                helperText={"To trigger a \"Go To\" to the currently selected location via MQTT or REST, simply use this payload."}
                coordinatesWarning={true}
                payload={integrationHelpDialogPayload}
            />
        </>
    );
};

export default GoToActions;
