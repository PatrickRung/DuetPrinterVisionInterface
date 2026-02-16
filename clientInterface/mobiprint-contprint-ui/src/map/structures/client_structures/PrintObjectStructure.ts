import ZoneClientStructure from "./ZoneClientStructure";
import {Canvas2DContextTrackingWrapper} from "../../utils/Canvas2DContextTrackingWrapper";
import robotPrintBed from "../icons/print-bed.svg";

const areaImage = new Image();
areaImage.src = robotPrintBed;

export class PrintObjectStructure extends ZoneClientStructure {
    constructor(
        x0: number, y0: number,
        x1: number, y1: number,
        active?: boolean
    ) {
        super(x0, y0, x1, y1, true);
        console.log("create")
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

        const ctx = ctxWrapper.getContext();
        ctx.drawImage(areaImage, p1.x - areaImage.width / 2, p0.y - areaImage.height / 2, Math.abs(p0.x - p1.x), Math.abs(p0.x - p1.x))
    }
}