import { useEffect, useRef } from "react";

const COLORS = {
  wall: "#333333",
  segment: "#d0e6ff",
  path: "#ff0000",
  charger: "#00aa00",
  robot: "#0000ff"
};

export default function ValetudoMapCanvas({ mapData }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!mapData) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const { size, pixelSize, layers, entities } = mapData;

    // Scale map down to something reasonable
    const SCALE = 0.15;

    canvas.width = size.x * SCALE;
    canvas.height = size.y * SCALE;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Helper: draw compressed pixels
    const drawCompressedPixels = (compressedPixels, color) => {
      ctx.fillStyle = color;

      for (let i = 0; i < compressedPixels.length; i += 3) {
        const x = compressedPixels[i];
        const y = compressedPixels[i + 1];
        const count = compressedPixels[i + 2];

        for (let dx = 0; dx < count; dx++) {
          ctx.fillRect(
            (x + dx) * pixelSize * SCALE,
            y * pixelSize * SCALE,
            pixelSize * SCALE,
            pixelSize * SCALE
          );
        }
      }
    };

    // 1️⃣ Draw layers
    for (const layer of layers) {
      if (layer.type === "wall") {
        drawCompressedPixels(layer.compressedPixels, COLORS.wall);
      }

      if (layer.type === "segment") {
        drawCompressedPixels(layer.compressedPixels, COLORS.segment);
      }
    }

    // 2️⃣ Draw entities
    for (const entity of entities) {
      if (entity.type === "path") {
        ctx.strokeStyle = COLORS.path;
        ctx.lineWidth = 2;
        ctx.beginPath();

        for (let i = 0; i < entity.points.length; i += 2) {
          const x = entity.points[i] * SCALE;
          const y = entity.points[i + 1] * SCALE;

          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }

      if (entity.type === "charger_location") {
        const [x, y] = entity.points;
        ctx.fillStyle = COLORS.charger;
        ctx.beginPath();
        ctx.arc(x * SCALE, y * SCALE, 6, 0, Math.PI * 2);
        ctx.fill();
      }

      if (entity.type === "robot_position") {
        const [x, y] = entity.points;
        ctx.fillStyle = COLORS.robot;
        ctx.beginPath();
        ctx.arc(x * SCALE, y * SCALE, 6, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }, [mapData]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        border: "1px solid #ccc",
        background: "#ffffff"
      }}
    />
  );
}