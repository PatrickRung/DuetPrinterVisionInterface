// File modified from format seen in https://github.com/cosdensolutions/code/tree/master/videos/long/react-upload-files-tutorial

import axios from 'axios';
import { ChangeEvent, useState } from 'react';
import {} from "../map/structures/map_structures/RobotPositionMapStructure";

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

var fileData: File;

export function getCurrentFile() : File {
  return fileData
}

export async function slice() {
    console.log("try")
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
            console.log(attrib);
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