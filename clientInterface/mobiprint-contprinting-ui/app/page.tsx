"use client";
import Image from "next/image";
import fetchMap from "./src/mapHandler/mapFetcher"
import { useEffect, useState } from 'react';
import PreviewLiveMap from "./src/mapping/PreviewLiveMap";
import ValetudoMapCanvas from "./src/mapHandler/valetudoMapCanvas"

export default function Home() {
const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadMap() {
      try {
        const res = await fetch('/api/robot-map');

        if (!res.ok) {
          throw new Error('Failed to load map');
        }

        const mapDat = await res.json();
        setData(mapDat)
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadMap();
  }, []);

  if (loading) return <div>Loading robot map…</div>;
  if (error) return <div>Error: {error}</div>;


  console.log("Data received from API call " + data)


  return (
    <main style={{ padding: 20 }}>
      <h1>Roborock IP: {process.env.NEXT_PUBLIC_IP_ADDRESS}</h1>
      <h1>Roborock API key: {process.env.NEXT_PUBLIC_API_KEY}</h1>
      <h1>Robot Map State</h1>
      <ValetudoMapCanvas mapData={data} />
    </main>
  );
}
