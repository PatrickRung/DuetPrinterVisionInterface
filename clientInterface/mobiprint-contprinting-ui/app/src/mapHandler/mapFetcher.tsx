import { useEffect, useState } from "react";

const createAPICall = async () => {

    const res = await fetch("http://192.168.2.29/api/v2/robot/state/map");

    // Print status
    console.log("Status:", res.status, res.statusText);

    // Print headers
    console.log("Headers:");
    for (const [key, value] of res.headers.entries()) {
    console.log(`${key}: ${value}`);
    }

    // Print body
    const body = await res.text();
    console.log("Body:");
    console.log(body);
}



// Recursive funcntion to fetch map data until received
function fetchMap() {
    console.log("go here")
    const [isClient, setIsClient] = useState(false);

    // Every 10 seconds until we get a response try to get the map from the roborock
    useEffect(() => {
        console.log("try")
        const timer = setTimeout(() => {
        const res = createAPICall();
        console.log(typeof(res))
        console.log(res)


        }, 0);

        return () => clearTimeout(timer); // cleanup
    }, []);

    if (!isClient) {
        return <div>Loading</div>;
    }

    return <div>Check logs</div>;
}

export default fetchMap;