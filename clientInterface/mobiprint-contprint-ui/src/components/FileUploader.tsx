// File modified from format seen in https://github.com/cosdensolutions/code/tree/master/videos/long/react-upload-files-tutorial
// NOTE FOR THIS FILE
// at some point PLEASE PLEASE PLEASE move the math to another folder, this file is way to large and complicated
import axios from 'axios';
import { ChangeEvent, useState } from 'react';
import { WIDTH_CONSTANT, LENGTH_CONSTANT } from "../map/structures/map_structures/RobotPositionMapStructure";  // When we slice we want to know how many segments
import { NoPhotography, StayCurrentPortraitOutlined, X } from '@mui/icons-material';
                                                                                              // to chunk up to relative to the print size thus
                                                                                              // we need this
import { getStructureManager, getCtxWrapper } from "../map/BaseMap"
import LocationMarkersStucture from "../map/structures/client_structures/LocationMarkersStucture"
import { getRobotAngleFromVector } from "../api/geomHelper"
import { sliceData } from "../api/raspi"
import { getPointsAlongCurve, getPoints } from "./componentHelpers/lineParser"
import { multiPointGoToRef } from "../map/actions/live_map_actions/GoToActionsMultiple"
import { PrintObjectStructure } from "../map/structures/client_structures/PrintObjectStructure"

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

  if (fileData !== null) {
    let SVGFileDataText = await fileData.text()

    // Compile all required data
    var parser = new DOMParser();
    let XMLRep = parser.parseFromString(SVGFileDataText, "text/xml")
    const svgElement = XMLRep.documentElement
    const widthStringRep = svgElement.getAttribute("width")
    const heightStringRep = svgElement.getAttribute("height")

    if (widthStringRep === null || 
      heightStringRep === null) {
      console.error("file incorrect");
      return;
    }

    let SVGWidth = parseInt(widthStringRep);
    let SVGHeight = parseInt(heightStringRep);

    // Refetch in case it does not exist
    structureManagerRef = getStructureManager()

    // Retreive data about image in browser sapce
    let boundingBoxRef = structureManagerRef.getClientStructures().find(
      (structure): structure is PrintObjectStructure => { return structure instanceof PrintObjectStructure });

    if (boundingBoxRef === undefined) {
      throw Error("No Bounding box found on UI, was the SVG uploaded and placed on the map?")
    }

    let inMapBoundingBoxDim = {x: Math.abs(boundingBoxRef.x0 - boundingBoxRef.x1), y: Math.abs(boundingBoxRef.y0 - boundingBoxRef.y1)}

    let topLeftCoordCM = getStructureManager().convertPixelCoordinatesToCMSpace({x: boundingBoxRef.x0, y: boundingBoxRef.y0})

    // Empty javascript object for building out the Json
    let slicingDataJson = {
      'SVGData': SVGFileDataText,
      "SVGWidthCM": inMapBoundingBoxDim.x,
      "SVGHeightCM": inMapBoundingBoxDim.y,
      "printBedWidthCM": WIDTH_CONSTANT,
      "printBedHeightCM": LENGTH_CONSTANT,
      "bedXOffsetCM": topLeftCoordCM.x,
      "bedYOffsetCM": topLeftCoordCM.y
    } 

    let slicingData = JSON.stringify(slicingDataJson)
    console.log(slicingData)

    let slicingResult = sliceData(slicingData)
    console.log(slicingResult)
  }
  else {
    console.log("No File Loaded! Upload a file to slice")
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
    console.log(typeof fileData)
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