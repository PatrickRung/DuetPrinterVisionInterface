import ClientStructure from "./ClientStructure";
import goToTargetIconSVG from "../icons/PotentialStateRobot.svg";
import {Canvas2DContextTrackingWrapper} from "../../utils/Canvas2DContextTrackingWrapper";
import {considerHiDPI} from "../../utils/helpers";

const img = new Image();
img.src = goToTargetIconSVG;

class LocationMarkerStructure extends ClientStructure {
    public static readonly TYPE = "GoToTargetClientStructure";
    rotation_: number;
    offset_: number;

    // Note about angle, 0 degrees is to the left and 90 degrees is straight down, these are both 
    // relative to the map
    // Offset is in map pixelspace distances
    constructor(x0: number, y0: number, rotation: number, offset: number) {
        super(x0, y0);
        this.rotation_ = rotation;
        this.offset_ = offset;
    }

    draw(ctxWrapper: Canvas2DContextTrackingWrapper, transformationMatrixToScreenSpace: DOMMatrixInit, scaleFactor: number): void {
        const ctx = ctxWrapper.getContext();
        const p0 = new DOMPoint(this.x0, this.y0).matrixTransform(transformationMatrixToScreenSpace);

        const scaledSize = {
            width: considerHiDPI(img.width) / (considerHiDPI(7) / scaleFactor),
            height: considerHiDPI(img.height) / (considerHiDPI(7) / scaleFactor)
        };

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

        const rotatedImg = rotateRobot(
            this.getOptimizedImage(img, scaledSize.width, scaledSize.height),
            scaledSize,
            (this.rotation_ + 90)
        );

        ctx.drawImage(
            rotatedImg,
            p0.x - scaledSize.width / 2,
            p0.y - scaledSize.height / 2,
            scaledSize.width,
            scaledSize.height
        );
    }
}

export default LocationMarkerStructure;
