import ZoneClientStructure from "./ZoneClientStructure";
import {Canvas2DContextTrackingWrapper} from "../../utils/Canvas2DContextTrackingWrapper";
import robotPrintBed from "../icons/print-bed.svg";
import getCurrentFile from "../../../components/FileUploader"
import { DataThresholdingSharp } from "@mui/icons-material";

const areaImage = new Image();
// Default image
areaImage.src = robotPrintBed;

export class PrintObjectStructure extends ZoneClientStructure {

    file: File | null;

    constructor(
        x0: number, y0: number,
        x1: number, y1: number,
        file: File,
        active?: boolean
    ) {
        super(x0, y0, x1, y1, true);
        
        if (typeof file !== "undefined") {
            const url = URL.createObjectURL(file);
            areaImage.src = url;
            this.file = file;
        }
        else {
            this.file = null;
        }
    }

    draw(ctxWrapper: Canvas2DContextTrackingWrapper, transformationMatrixToScreenSpace: DOMMatrixInit, scaleFactor: number, pixelSize: number): void {
        super.draw(ctxWrapper, transformationMatrixToScreenSpace, scaleFactor, pixelSize);
        console.log("this happen")
        
        // Draw the outline first, then add the SVG that we want to place
        // This process is acurate to the real world space and thus will allow users to gauge 
        // what the print looks like as well as for the slicer to figure out the destinations and pass it to the
        // multi go to command

        const p0 = new DOMPoint(this.x0, this.y0).matrixTransform(transformationMatrixToScreenSpace);
        const p1 = new DOMPoint(this.x1, this.y1).matrixTransform(transformationMatrixToScreenSpace);

        let spaceWidth = Math.abs(p0.x - p1.x);
        let spaceHeight = Math.abs(p0.x - p1.x)

        const ctx = ctxWrapper.getContext();

        let scaledWidth = areaImage.width * scaleFactor
        let scaledHeight = areaImage.height * scaleFactor

        let scaleOfBoundingX = Math.abs(this.x0 - this.x1)
        let scaleOfBoundingY = Math.abs(this.y0 - this.y1)
        
        // Scales proportional to the top of placement
        ctx.drawImage(areaImage, p1.x - spaceHeight, p0.y, scaleOfBoundingX * scaleFactor, scaleOfBoundingY * scaleFactor)
    }
}