// File modified from format seen in https://github.com/cosdensolutions/code/tree/master/videos/long/react-upload-files-tutorial
// NOTE FOR THIS FILE
// at some point PLEASE PLEASE PLEASE move the math to another folder, this file is way to large and complicated
import axios from 'axios';
import { ChangeEvent, useState } from 'react';
import { WIDTH_CONSTANT, OFFSET } from "../map/structures/map_structures/RobotPositionMapStructure";  // When we slice we want to know how many segments
import { NoPhotography, StayCurrentPortraitOutlined, X } from '@mui/icons-material';
                                                                                              // to chunk up to relative to the print size thus
                                                                                              // we need this
import { getStructureManager, getCtxWrapper } from "../map/BaseMap"
import LocationMarkersStucture from "../map/structures/client_structures/LocationMarkersStucture"
import { getRobotAngleFromVector } from "../api/geomHelper"
import { sliceData } from "../api/raspi"
import { getPointsAlongCurve, getPoints } from "./componentHelpers/lineParser"
import { multiPointGoToRef } from "../map/actions/live_map_actions/GoToActionsMultiple"

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

var fileData: File;
var SVGWidth: number
var SVGHeight: number

var structureManagerRef = getStructureManager()

// Debug vars
const SHOW_SEGMENT_LOCATION = true;

export function getCurrentFile() : File {
  return fileData
}

export async function slice() {

  let testingText = '{ "employees" : [' +
  '{ "firstName":"John" , "lastName":"Doe" },' +
  '{ "firstName":"Anna" , "lastName":"Smith" },' +
  '{ "firstName":"Peter" , "lastName":"Jones" } ]}';
  const jsonObj = JSON.parse(testingText);
  sliceData("test")

  // Verify structure manager exists
  structureManagerRef = getStructureManager();
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

      // ACCOUNT FOR CIRCLE CASE
      // Check for existance of circle and if so, generate points based on properties of circle and then
      // return to not parse the line method
      let circleXMLRef = XMLRep.getElementsByTagName("circle")
      if (typeof circleXMLRef !== "undefined" && circleXMLRef.length > 0) {
        let circleRef = circleXMLRef[0]
        
        let centerOfCircle = new DOMPoint(circleRef.cx.baseVal.value, circleRef.cy.baseVal.value);
        let radius = circleRef.r.baseVal.value;
        
        // Discretize 16 points along the circle in order to convert them to points to be parsed later on
        for (let i = 0; i < 16; i++) {
          let currPoint = new DOMPoint(centerOfCircle.x + (Math.cos(i * (2 / 16 * Math.PI)) * radius),
            centerOfCircle.y + (Math.sin(i * (2 / 16 * Math.PI))) * radius)
          points.push(currPoint)
        }
        points.push(new DOMPoint(centerOfCircle.x + (Math.cos(0) * radius),
            centerOfCircle.y + (Math.sin(0)) * radius))
        console.log(points)
      }
      else {
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
      }

      console.log(points)
    }

    // Generate path from points and generate destinations based on bed size
    if (points.length > 0) {

      let segmentsEdge: Array<DOMPoint> | undefined = getPointsAlongCurve(points, WIDTH_CONSTANT, SVGWidth, SVGHeight, SHOW_SEGMENT_LOCATION);

      if (typeof segmentsEdge === "undefined") {
        console.error("segmented edges returned incorrectly")
        return;
      }

      console.log("out " + segmentsEdge.length)
      console.log(segmentsEdge)

      let offsetInPixelSpace = getStructureManager().convertCMLengthToPixelSpace(OFFSET)

      // Iterate through points (considers two adjacent points and formulates position perpendicular to both)
      for (let pointIndex = 0; pointIndex < segmentsEdge.length; pointIndex++) {

        // Get vector between points
        let p1;
        let p2;

        if (pointIndex < segmentsEdge.length - 1) {
          p1 = segmentsEdge[pointIndex];
          p2 = segmentsEdge[pointIndex + 1];
        }
        else {
          // Last case which uses same tangent however uses last point as print location
          p1 = segmentsEdge[pointIndex - 1];
          p2 = segmentsEdge[pointIndex];
        }

        let vec = new DOMPoint(p2.x - p1.x, p2.y - p1.y);
        let halfWayPoint;
        if (pointIndex < segmentsEdge.length - 1) {
          halfWayPoint = new DOMPoint(p1.x + (vec.x / 2), p1.y + (vec.y / 2));
        }
        else {
          halfWayPoint = p2;
        }
        let perpVec = new DOMPoint(vec.y, -vec.x);

        // Get unit vec of perpendicular vector
        let perpVecMag = Math.sqrt(Math.pow(perpVec.x, 2) + Math.pow(perpVec.y, 2));
        perpVec = new DOMPoint(perpVec.x / perpVecMag, perpVec.y / perpVecMag);

        let robotAoa = getRobotAngleFromVector(perpVec)
        robotAoa -= 180;
        console.log("aoa " + robotAoa)
        
        let robotLocX = halfWayPoint.x + (perpVec.x * offsetInPixelSpace);
        let robotLocY = halfWayPoint.y + (perpVec.y * offsetInPixelSpace);

        structureManagerRef.addClientStructure(
          new LocationMarkersStucture(robotLocX, 
          robotLocY, robotAoa, offsetInPixelSpace))

        // Add to multiGoto point as well to print
        multiPointGoToRef.addDestination(halfWayPoint.x, halfWayPoint.y, robotAoa);
      }
      console.log(multiPointGoToRef)
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