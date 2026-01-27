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

class MultiPointGoToState {

    // Properties
    destinationsForRoborock : GoToTargetClientStructure[];
    currDestination : GoToTargetClientStructure | undefined;
    prevPoint: number[] | null;
    structureManagerRef: StructureManager | null;
    existingTimer: boolean;                                 // Denotes whether or not there is a timer active 
                                                            // !! DO NOT CREATED MULTIPLE TIMERS CHECK THIS VAR
    withinDesiredAreaCount: number

    constructor() {
        this.destinationsForRoborock = [];
        this.prevPoint = null;
        this.currDestination = undefined;
        this.structureManagerRef = getStructureManager();
        this.existingTimer = false;
        this.withinDesiredAreaCount = 0
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
            console.log("Stationary at " + getRoborockGlobalPos() + " : TIMESTAMP: " + Date.now())

            let pointsCM = this.structureManagerRef.convertPixelCoordinatesToCMSpace({x: this.currDestination.x0, y: this.currDestination.x0});
            console.log("Desired "  + pointsCM.x + " " + pointsCM.y)

            // Check if we reached destination (We accept anywhere within 100 CM range)
            let magDiff = Math.pow(Math.pow(currPoint[0] - pointsCM.x, 2) + Math.pow(currPoint[1] - pointsCM.y, 2), 0.5)
            if (this.currDestination != undefined && magDiff < 150) {

                // Update state
                this.withinDesiredAreaCount++;

                // Needs to stay at end poll for 3 loops
                if (this.withinDesiredAreaCount >= 5) {
                    this.existingTimer = false;
                    this.prevPoint = null;

                    console.log("DONE!");   
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
            this.destinationsForRoborock.push(goToTarget);
        }
    }

    executeConsecGoTo() {
        let recentGoTo = this.destinationsForRoborock.pop() 

        // Refetch structure manager
        this.structureManagerRef = getStructureManager();
        if (recentGoTo == undefined || 
            this.structureManagerRef == null || 
            this.existingTimer) {
                console.log("terminate")
                return;
        }

        this.currDestination = recentGoTo;
        let CMCoords = this.structureManagerRef.convertPixelCoordinatesToCMSpace({x: recentGoTo.x0, y: recentGoTo.y0})
        sendGoToCommand(CMCoords);
        this.withinDesiredAreaCount = 0;

        this.initiateGoToCommandChecker()
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
    if (typeof goToTarget !== "undefined") {
        multiPointGoToRef.updateDestinations(goToTarget);
    }

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
