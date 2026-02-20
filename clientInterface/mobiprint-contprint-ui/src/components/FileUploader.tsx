// File modified from format seen in https://github.com/cosdensolutions/code/tree/master/videos/long/react-upload-files-tutorial

import axios from 'axios';
import { ChangeEvent, useState } from 'react';
import { WIDTH_CONSTANT } from "../map/structures/map_structures/RobotPositionMapStructure";  // When we slice we want to know how many segments
import { NoPhotography, StayCurrentPortraitOutlined, X } from '@mui/icons-material';
                                                                                              // to chunk up to relative to the print size thus
                                                                                              // we need this
import { getStructureManager, getCtxWrapper } from "../map/BaseMap"
import LocationMarkersStucture from "../map/structures/client_structures/LocationMarkersStucture"
import { PrintObjectStructure } from "../map/structures/client_structures/PrintObjectStructure"
import { BoundFunction } from '@testing-library/dom';
import { renderToPipeableStream } from 'react-dom/server';
import Structure from '../map/structures/Structure';

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

var fileData: File;
var SVGWidth: number
var SVGHeight: number
const ITERATOR_HARDCAP_CONSTANT = 100

var structureManagerRef = getStructureManager()

export function getCurrentFile() : File {
  return fileData
}

function getDistance(p1: DOMPoint, p2: DOMPoint): number {
  if (typeof p1 === "undefined") {
    throw Error("p1 coordinate undefined")
  }
  if (typeof p2 === "undefined") {
    throw Error("p2 coordinate undefined")
  }
  return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2))
}

function getPointsAlongCurve(curvePoints: Array<DOMPoint>, length: number): Array<DOMPoint> | undefined {

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
  structureManagerRef.addClientStructure(new LocationMarkersStucture(currPoint.x,
                                                                      currPoint.y))

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
          structureManagerRef.addClientStructure(new LocationMarkersStucture(currPoint.x, currPoint.y))
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
    structureManagerRef.addClientStructure(new LocationMarkersStucture(currPoint.x, currPoint.y))
    segments.push();
  }
  console.log("finished slicing")
  return segments;
}

function getPoints(coordinatesAttrib: string) : Array<DOMPoint> {
  let indexOfC = -1
  let points = new Array<DOMPoint> ;
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
      console.log(XCoord)
      console.log(YCoord)

      if (XCoord !== undefined && YCoord != undefined) {
        console.log("make")
        points.push(new DOMPoint(parseInt(XCoord), parseInt(YCoord)))
      }
    }
  }
  return points;
}

export async function slice() {
    console.log("try")

    // State for the slicing process
    let points: Array<DOMPoint> = [];

    if (fileData !== null) {
        let text = await fileData.text()

        var parser = new DOMParser();
        let XMLRep = parser.parseFromString(text, "text/xml")
        const svgElement = XMLRep.documentElement
        const widthStringRep = svgElement.getAttribute("width")
        const heightStringRep = svgElement.getAttribute("height")

        if (widthStringRep === null || 
          heightStringRep === null) {
          console.error("file incorrect");
          return;
        }

        SVGWidth = parseInt(widthStringRep);
        SVGHeight = parseInt(heightStringRep);
        

        // Parse path
        // Requires path that are placed in front to have a ID adjacent and greatrer than (be placed below in the XML)
        // in order for paths to be placed in order and concatenated
        let line = XMLRep.getElementsByTagName("path")
        // Mark as parsed
        for (let index = 0; index < line.length; index++) {
            let currLine = line.item(index);
            let attrib = currLine?.getAttribute("d")
            if (attrib != null) {
              let res = getPoints(attrib);
              points = points.concat(res);
            }
        }
        console.log(points)
    }

    // Generate path from points and generate destinations based on bed size
    if (points.length > 0) {
      let finishedPath = false;

      // Last index of spot not covered by print area
      let currsCoveredSpot = 0

      let segmentsEdge: Array<DOMPoint> | undefined = getPointsAlongCurve(points, WIDTH_CONSTANT);

      if (typeof segmentsEdge === "undefined") {
        console.error("segmented edges returned incorrectly")
      }


    }

}

export default function FileUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<UploadStatus>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  }

  // XML parsing inspired by https://stackoverflow.com/questions/17604071/parse-xml-using-javascript
  async function handleFileUpload() {
    if (!file) return;

    fileData = file

    setStatus('success')
  }

  return (
    <div className="space-y-2">
      <input type="file" onChange={handleFileChange} />

      {file && (
        <div className="mb-4 text-sm">
          <p>File name: {file.name}</p>
          <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
          <p>Type: {file.type}</p>
        </div>
      )}

      {status === 'uploading' && (
        <div className="space-y-2">
          <div className="h-2.5 w-full rounded-full bg-gray-200">
            <div
              className="h-2.5 rounded-full bg-blue-600 transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        </div>
      )}

      {file && status !== 'uploading' && (
        <button onClick={handleFileUpload}>Upload</button>
      )}

      {status === 'success' && (
        <p className="text-sm text-green-600">File parsed</p>
      )}

      {status === 'error' && (
        <p className="text-sm text-red-600">Upload failed. Please try again.</p>
      )}
    </div>
  );
}