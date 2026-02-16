import MapStructure from "./MapStructure";
import robotIconSVG from "../icons/robot.svg";
import robotPrintBed from "../icons/print-bed.svg";
import {Canvas2DContextTrackingWrapper} from "../../utils/Canvas2DContextTrackingWrapper";
import {considerHiDPI} from "../../utils/helpers";
import { getStructureManager } from "../../BaseMap" // Get strucutre manager from base map in order 
import StructureManager from "../../StructureManager";
import { Co2Sharp } from "@mui/icons-material";

const img = new Image();
img.src = robotIconSVG;

const areaImage = new Image();
areaImage.src = robotPrintBed;

// These constants are used code wide
export const WIDTH_CONSTANT = 40
export const LENGTH_CONSTANT = 20

export const OFFSET = 30           // OFFSET is declared in CM
export const BED_ANGLE = 90       // Bed is located 

class RobotPositionMapStructure extends MapStructure {
    public static readonly TYPE = "RobotPositionMapStructure";

    private readonly angle: number;
    private structureManagerRef: StructureManager;

    constructor(x0 : number ,y0 : number, angle: number) {
        super(x0, y0);

        this.angle = angle;
        this.structureManagerRef = getStructureManager()
    }

    draw(ctxWrapper: Canvas2DContextTrackingWrapper, transformationMatrixToScreenSpace: DOMMatrixInit, scaleFactor: number): void {
        const scaledSize = {
            width: considerHiDPI(img.width) / (considerHiDPI(4.5) / scaleFactor),
            height: considerHiDPI(img.height) / (considerHiDPI(4.5) / scaleFactor)
        };

        const printAreaScaledSize = {
            width: considerHiDPI(areaImage.width) / (considerHiDPI(4.5) / scaleFactor),
            height: considerHiDPI(areaImage.height) / (considerHiDPI(4.5) / scaleFactor)
        };

        if (scaledSize.width < 1 || scaledSize.height < 1) {
            return;
        }

        const rotateRobot = (source: CanvasImageSource, size: {width: number, height: number}, angle: number) => {
            const canvasWidth = Math.round(size.width);
            const canvasHeight = Math.round(size.height);

            const canvasimg = document.createElement("canvas");
            canvasimg.width = canvasWidth;
            canvasimg.height = canvasHeight;
            const ctximg = canvasimg.getContext("2d");

            if (ctximg) {
                ctximg.translate(canvasWidth / 2, canvasHeight / 2);
                ctximg.rotate(angle * Math.PI / 180);
                ctximg.translate(-canvasWidth / 2, -canvasHeight / 2);
                ctximg.drawImage(source, 0, 0, canvasWidth, canvasHeight);
            }

            return canvasimg;
        };

        // Used to compensate for the fact that the roborock print base is larger than the bounding box for the static image
        // compensates by adding more height and width if base exceeds icon width/ height
        const rotatePrintBox = (source: CanvasImageSource, size: {width: number, height: number}, angle: number) => {

            // Really janky solution that might not even work as the squish is a little weird
            const bedsizeScreenSpaceOffset = new DOMPoint(this.structureManagerRef.convertCMLengthToPixelSpace(WIDTH_CONSTANT), 
                this.structureManagerRef.convertCMLengthToPixelSpace(LENGTH_CONSTANT)).matrixTransform(transformationMatrixToScreenSpace);
            const zeroCoord = new DOMPoint(0,0).matrixTransform(transformationMatrixToScreenSpace);

            const bedsizeScreenSpace = new DOMPoint(bedsizeScreenSpaceOffset.x - zeroCoord.x, bedsizeScreenSpaceOffset.y - zeroCoord.y);
            const radians = angle * Math.PI / 180;

            const originalWidth = bedsizeScreenSpace.x;
            const originalHeight = bedsizeScreenSpace.y;

            // Calculate bounding box size after rotation
            const cos = Math.abs(Math.cos(radians));
            const sin = Math.abs(Math.sin(radians));

            const newWidth = Math.ceil(originalWidth * cos + originalHeight * sin);
            const newHeight = Math.ceil(originalWidth * sin + originalHeight * cos);

            const canvasimg = document.createElement("canvas");
            canvasimg.width = newWidth;
            canvasimg.height = newHeight;

            const ctximg = canvasimg.getContext("2d");

                if (ctximg) {
                    // Move to center of new canvas
                    ctximg.translate(newWidth / 2, newHeight / 2);

                    // Rotate
                    ctximg.rotate(radians);

                    // Draw image centered
                    ctximg.drawImage(
                        source,
                        -originalWidth / 2,
                        -originalHeight / 2,
                        originalWidth,
                        originalHeight
                    );
                }

            return canvasimg;
        };

        const rotatedImg = rotateRobot(
            this.getOptimizedImage(img, scaledSize.width, scaledSize.height),
            scaledSize,
            this.angle
        );

        const rotatedPrintSpaceImg = rotatePrintBox(
            areaImage,
            printAreaScaledSize,
            this.angle
        );

        const ctx = ctxWrapper.getContext();
        const p0 = new DOMPoint(this.x0, this.y0).matrixTransform(transformationMatrixToScreenSpace);

        ctx.drawImage(
            rotatedImg,
            p0.x - rotatedImg.width / 2,
            p0.y - rotatedImg.height / 2,
            rotatedImg.width,
            rotatedImg.height
        );

        // Make offset calculation in the map pixel coordinate space, then use the matrix transform to transpose into screen pixel size
        const offSetLoc = new DOMPoint(this.x0 + Math.cos((this.angle + 90) * Math.PI / 180) * this.structureManagerRef.convertCMLengthToPixelSpace(OFFSET), 
            this.y0 + Math.sin((this.angle + 90) * Math.PI / 180) * this.structureManagerRef.convertCMLengthToPixelSpace(OFFSET)).matrixTransform(transformationMatrixToScreenSpace);

        ctx.drawImage(
            rotatedPrintSpaceImg,
            offSetLoc.x - rotatedImg.width / 2,
            offSetLoc.y - rotatedImg.height / 2,
            rotatedImg.width,
            rotatedImg.height
        );
    }
}

export default RobotPositionMapStructure;
