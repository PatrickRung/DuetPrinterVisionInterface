// File modified from format seen in https://github.com/cosdensolutions/code/tree/master/videos/long/react-upload-files-tutorial

import axios from 'axios';
import { ChangeEvent, useState } from 'react';
import { WIDTH_CONSTANT } from "../map/structures/map_structures/RobotPositionMapStructure";  // When we slice we want to know how many segments
import { X } from '@mui/icons-material';
                                                                                              // to chunk up to relative to the print size thus
                                                                                              // we need this

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

var fileData: File;

export function getCurrentFile() : File {
  return fileData
}

function getDistance(p1: {x: number, y: number}, p2: {x: number, y: number}): number {
  return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2))
}

function getPoints(coordinatesAttrib: string) : Array<{x: number, y: number}> {
  let indexOfC = -1
  let points = new Array<{x: number, y: number}> ;
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
        points.push({x: parseInt(XCoord), y: parseInt(YCoord)})
      }
    }
  }
  return points;
}

export async function slice() {
    console.log("try")

    // State for the slicing process
    let points: Array<{x: number, y: number}> = [];

    if (fileData !== null) {
        let text = await fileData.text()

        var parser = new DOMParser();
        let XMLRep = parser.parseFromString(text, "text/xml")

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

      while (!finishedPath) {

        let printSpaceRemaining = WIDTH_CONSTANT;

        while (printSpaceRemaining > 0) {

          let currPoint = points[currsCoveredSpot]
          let nextPoint = points[currsCoveredSpot + 1]

          // let distToNext = getDistance()
          // if ()
        }
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