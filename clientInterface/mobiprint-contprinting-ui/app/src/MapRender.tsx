import {RawMapData} from "./RawMapData";

export class Maprender {
    private readonly canvas: HTMLCanvasElement;
    private readonly ctx: CanvasRenderingContext2D;

    constructor() {
        this.canvas = document.createElement("canvas");
        this.ctx = this.canvas.getContext("2d")!; 
        // Note to self ! is the non null assertion, meaning that the return value of getContext will never be null
    }

    draw (data : RawMapData) {
        this.ctx.putImageData()
    }
}