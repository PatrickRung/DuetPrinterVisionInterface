
import { getStructureManager, getCtxWrapper } from "../../map/BaseMap"
import { PrintObjectStructure } from "../../map/structures/client_structures/PrintObjectStructure"
import GoToTargetClientStructure from "../../map/structures/client_structures/GoToTargetClientStructure"

var structureManagerRef = getStructureManager()

const ITERATOR_HARDCAP_CONSTANT = 100

function getDistance(p1: DOMPoint, p2: DOMPoint): number {
  if (typeof p1 === "undefined") {
    throw Error("p1 coordinate undefined")
  }
  if (typeof p2 === "undefined") {
    throw Error("p2 coordinate undefined")
  }
  return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2))
}

export function getPointsAlongCurve(curvePoints: Array<DOMPoint>, 
    length: number, 
    SVGWidth: number, 
    SVGHeight: number,
    SHOW_SEGMENT_LOCATION: boolean): Array<DOMPoint> | undefined {

  // Fetch data required for SVG to map display
  structureManagerRef = getStructureManager()
  if (typeof structureManagerRef === "undefined") {
    console.error("No structure manager initialized");
    return;
  }

  // Declare all state info regarding slicing
  let curvePointCurrIndex = 0
  let currPoint : DOMPoint
  let segments : Array<DOMPoint>  = [];
  let ctxWrapperRef = getCtxWrapper()
  let lengthInPixelSpace = structureManagerRef.convertCMLengthToPixelSpace(length);

  // Note about the code beow it uses type predicates where the param is still structure, but the follow "is" statement
  // enforces the type input of the function and thus the return type
  let boundingBoxRef = structureManagerRef.getClientStructures().find(
    (structure): structure is PrintObjectStructure => { return structure instanceof PrintObjectStructure });

  if (boundingBoxRef === undefined) {
    throw Error("No Bounding box found on UI, was the SVG uploaded and placed on the map?")
  }

  let inMapBoundingBoxDim = {x: Math.abs(boundingBoxRef.x0 - boundingBoxRef.x1), y: Math.abs(boundingBoxRef.y0 - boundingBoxRef.y1)}

  let topLeftCoord = new DOMPoint(boundingBoxRef.x0, boundingBoxRef.y0)

  // Convert all points to be in the same coordinate space
  for (let i = 0; i < curvePoints.length; i++) {

    // iteration points are essentialy the percent of the bounding box covers
    let iterationPoint = curvePoints.at(i);
    
    if (typeof iterationPoint !== "undefined") {
      let coordInMapPixelSpace = {x: (iterationPoint.x / SVGWidth) * inMapBoundingBoxDim.x,
        y: (iterationPoint.y / SVGHeight) * inMapBoundingBoxDim.y}
      curvePoints[i] = new DOMPoint(topLeftCoord.x + coordInMapPixelSpace.x, topLeftCoord.y + coordInMapPixelSpace.y);
    }
  }

  let tempPoint = curvePoints.at(0)

  if (typeof tempPoint === "undefined") {
    throw Error("Invliad points")
  }

  currPoint = tempPoint;
  segments.push(currPoint)

  // Enforce hard cap to how many iterations can happen to avoid runnaway looping
  let hardCapIterator = 0
  
  while (curvePointCurrIndex < curvePoints.length) {
    hardCapIterator++
    if (hardCapIterator >= ITERATOR_HARDCAP_CONSTANT) {
      throw Error("Passed iterator hardcap, this print might just be very large (increasee hard cap) or this loop went on for longer than " 
        + ITERATOR_HARDCAP_CONSTANT)
      return;
    }

    let p2 = curvePoints.at(curvePointCurrIndex + 1)

    if (typeof currPoint === "undefined") {
      console.error("P1 undefined, bad list?")
      break;
    }
    if (typeof p2 === "undefined") {
      console.error("P2 undefined, bad list?")
      break;
    }

    // Draw the current point
    let currDistance = getDistance(currPoint, p2)

    // Handle cases
    console.log("out " + (currDistance - lengthInPixelSpace));
    console.log("curr " + currPoint);
    console.log("p2 " + p2);

    // If print segment shorter than current line
    if (currDistance - lengthInPixelSpace > 0) {
      // Get unit vector and multiply (divde delta by mag)
      let unitVec = {x: (p2.x - currPoint.x) / currDistance, y: (p2.y - currPoint.y) / currDistance}

      // Rescale to be desired length and apply offset
      currPoint = new DOMPoint(currPoint.x + (unitVec.x * lengthInPixelSpace), 
        currPoint.y + (unitVec.y * lengthInPixelSpace));  
    }
    else {
      let lengthRemaining = lengthInPixelSpace;

      let totalPassed = 0;

      console.log("come here")
      console.log(p2)
      console.log(currPoint)

      // In this case iterate through points until entire print space is covered
      while (lengthRemaining > 0) {

        // Reached end of line just return
        if (typeof p2 === "undefined") {
          return segments;
        }

        // Recaulcate currDistance
        currDistance = getDistance(currPoint, p2)

        lengthRemaining -= currDistance;

        if (lengthRemaining < 0) {
          // Get unit vector and multiply (divde delta by mag)
          let unitVec = {x: (p2.x - currPoint.x) / currDistance, y: (p2.y - currPoint.y) / currDistance}

          // Rescale to be desired length
          currPoint = new DOMPoint(currPoint.x + (unitVec.x * (lengthInPixelSpace - totalPassed)), 
            currPoint.y + (unitVec.y * (lengthInPixelSpace - totalPassed)));          
        }
        else {
          curvePointCurrIndex++;

          // Update point objects
          currPoint = curvePoints[curvePointCurrIndex]
          p2 = curvePoints[curvePointCurrIndex + 1]
          totalPassed += currDistance;
        }
      }
      
    }
    segments.push(currPoint);
    if (SHOW_SEGMENT_LOCATION) {
        // structureManagerRef.addClientStructure(new GoToTargetClientStructure(currPoint.x, currPoint.y))
    }
  }
  console.log("finished slicing")
  return segments;
}

/**
 * Froma a SVG entry convert the attribute into an array of DOMPoints for easier handling within code
 * @param {string} Coordinate attributes taken straight out of the SVG
 * @returns {Array<DOMPoint>} List of points that contian contained within the line
 */
export function getPoints(coordinatesAttrib: string) : Array<DOMPoint> {
  let indexOfC = -1
  let points = new Array<DOMPoint>;
  for (let i = 0; i < coordinatesAttrib.length; i++) {
    if (coordinatesAttrib.at(i) === 'C') {
      indexOfC = i;
      break;
    }
  }

  if (indexOfC == -1) {
    throw new Error("Invalid SVG path (does not contain C denoted points)")
  }

  const coordsAmalgamatedString = coordinatesAttrib.substring(indexOfC + 1, coordinatesAttrib.length);
  const coordsSplit = coordsAmalgamatedString.split(", ")

  for (let i = 0; i < coordsSplit.length; i++) {
    let splitXY = coordsSplit.at(i)?.split(" ")
    if (typeof splitXY !== undefined) {
      let XCoord = splitXY?.at(0)
      let YCoord = splitXY?.at(1)

      if (XCoord !== undefined && YCoord != undefined) {
        points.push(new DOMPoint(parseInt(XCoord), parseInt(YCoord)))
      }
    }
  }
  return points;
}
