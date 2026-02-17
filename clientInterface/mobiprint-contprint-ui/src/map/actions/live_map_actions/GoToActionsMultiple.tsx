import {
    useGoToMutation,
    useRobotStatusQuery
} from "../../../api";
import React from "react";
import {CircularProgress, Grid2, Typography} from "@mui/material";
import {ActionButton} from "../../Styled";
import GoToTargetClientStructure from "../../structures/client_structures/GoToTargetClientStructure";
import IntegrationHelpDialog from "../../../components/IntegrationHelpDialog";
import StructureManager from "../../StructureManager";
import {useLongPress} from "use-long-press";
import {floorObject} from "../../../api/utils";
import {PointCoordinates} from "../../utils/types";
import { WIDTH_CONSTANT, LENGTH_CONSTANT, OFFSET } from "../../structures/map_structures/RobotPositionMapStructure"
import {
    Clear as ClearIcon,
    PlayArrow as GoIcon,
    Print,
    Circle as PrintIcon
} from "@mui/icons-material";
import {sendGoToCommand} from "../../../api/client"
import { roborockRotate } from "../../../api/CustomClient"
import { getStructureManager, getRoborockGlobalRot } from "../../BaseMap"
import { PrintObjectStructure } from "../../structures/client_structures/PrintObjectStructure"
import { slice } from "../../../components/FileUploader"

interface MultoGoToProperties {
    goToTarget: GoToTargetClientStructure | undefined;

    convertPixelCoordinatesToCMSpace(coordinates: PointCoordinates) : PointCoordinates

    onClear(): void;

    onClearPrint(): void;

    onAdd(): void;
}

// Path traverse state machine
const RobotGoToStates = Object.freeze({
    INIT: "Initalized",
    TRAVERSING: "Traversing",
    FIN: "Finished",
    NODEST: "No destination"
});

// Abstraction for print loc considering the location and area of attack
export class printLocation {
    x_: number
    y_: number
    aoa_: number
    constructor(x: number, y: number, aoa: number) {
        this.x_ = x;
        this.y_ = y;
        this.aoa_ = aoa;
    }
}

class MultiPointGoToState {

    // Properties
    destinationsForRoborock : printLocation[];
    currDestination : printLocation | undefined;
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
        this.hardCoded = false;
        this.currentTraverseState = RobotGoToStates.NODEST;
        if (this.hardCoded) {

            // Removed since old coordinates were not right type
            this.destinationsForRoborock = [];
        }
        else {
            this.destinationsForRoborock = [];
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
                checkAproxEquals(goToTarget.x0, currCoord.x_, 0.01) && 
                checkAproxEquals(goToTarget.y0, currCoord.y_, 0.01)) {
                    destContainsCoord = true;
            }
        }

        if (!destContainsCoord && typeof goToTarget !== "undefined") {
            console.log("Add " + goToTarget.x0 + ", " + goToTarget.y0)
            // Default angle set to 0, for demonstration purposes, the roborock should always look to the right of the screen
            let tempTarget = new printLocation(goToTarget.x0, goToTarget.y0, 0);
            this.destinationsForRoborock.push(tempTarget);
        }
    }

    async executeConsecGoTo() {
        console.log("Points left " + this.destinationsForRoborock.length)
        if (this.destinationsForRoborock.length == 0) {
            return;
        }

        // Pop off the target that we are going to right now
        let recentGoTo = this.destinationsForRoborock.shift() 

        // Refetch structure manager
        this.structureManagerRef = getStructureManager();
        if (recentGoTo == undefined || 
            this.structureManagerRef == null) {
                console.error("Tried to go to multiple with either existing path or unable to fetch required objects")
                return;
        }

        this.currDestination = recentGoTo;
        let CMCoords = this.structureManagerRef.convertPixelCoordinatesToCMSpace({x: recentGoTo.x_, y: recentGoTo.y_})

        // We want to figure out relative to the aoa where the destination is
        let destX = CMCoords.x + (OFFSET * Math.cos(recentGoTo.aoa_))
        let destY = CMCoords.y + (OFFSET * Math.sin(recentGoTo.aoa_ ))

        // Sending the go to command right away leads to issues, delay for 3 seconds
        setTimeout(() => {
            sendGoToCommand({x: destX, y: destY});
        }, 3000)

        this.currentTraverseState = RobotGoToStates.INIT;
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

                // Before moving on we want to rotate to the desired angle
                let currRot = getRoborockGlobalRot()

                // Add slight delay as sending too many commands breaks the backend
                setTimeout(() => {
                    if (typeof this.currDestination !== "undefined") {  // It WILL be defined however error is being thrown
                        roborockRotate(this.currDestination.aoa_ + 90);
                    }
                }, 500)

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
    props: MultoGoToProperties
): React.ReactElement => {
    // Create list for target points:
    const {goToTarget, convertPixelCoordinatesToCMSpace, onClear, onAdd, onClearPrint} = props;
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
                <Grid2>
                    {
                        <ActionButton
                            color="inherit"
                            size="medium"
                            variant="extended"
                            onClick={onAdd}
                        >
                            <PrintIcon style={{marginRight: "0.25rem", marginLeft: "-0.25rem"}}/>
                            Add print
                        </ActionButton>
                    }
                </Grid2>
                <Grid2>
                    {
                        <ActionButton
                            color="inherit"
                            size="medium"
                            variant="extended"
                            onClick={onClearPrint}
                        >
                            <PrintIcon style={{marginRight: "0.25rem", marginLeft: "-0.25rem"}}/>
                            Clear Print Area
                        </ActionButton>
                    }
                </Grid2>
               <Grid2>
                    {
                        <ActionButton
                            color="inherit"
                            size="medium"
                            variant="extended"
                            onClick={ slice }
                        >
                            <PrintIcon style={{marginRight: "0.25rem", marginLeft: "-0.25rem"}}/>
                            Slice
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