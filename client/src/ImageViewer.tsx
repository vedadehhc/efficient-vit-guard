
import React, { useRef, useState, useEffect } from 'react';
import { Box } from '@chakra-ui/layout';
import { Image as ImageUI } from '@chakra-ui/image';

interface ImageViewerProps {
    imageSrc: string;
    setDrawnBox: React.Dispatch<React.SetStateAction<DrawnBox | null>>;
  }

interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface DrawnBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

const ImageViewer: React.FC<ImageViewerProps> = ({imageSrc, setDrawnBox}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [drawing, setDrawing] = useState(false);
  const [startPoint, setStartPoint] = useState({ x: 0, y: 0 });
  const [image, setImage] = useState<HTMLImageElement | null>(null);

  useEffect(() => {
    const loadImage = async () => {
      const img = new Image();
      img.src = imageSrc;
      await img.decode();
      setImage(img);
    };

    loadImage();
  }, [imageSrc]);

  const drawWithBox = (box: BoundingBox | null) => {
    if (!image || !canvasRef.current) {
      return;
    }
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      const { width, height } = calculateFitSize(image.width, image.height, canvas.width, canvas.height);
      canvas.width = width;
      canvas.height = height;
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
      // ctx.drawImage(image, 0, 0, width, height);
      if (box) {
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        ctx.strokeRect(box.x, box.y, box.width, box.height);
      }
    }
  }

  useEffect(() => {
    drawWithBox(null);
  }, [image]);

  const calculateFitSize = (srcWidth: number, srcHeight: number, maxWidth: number, maxHeight: number) => {
    // return {width: srcWidth, height: srcHeight};
    const aspectRatio = srcWidth / srcHeight;
    const newWidth = Math.min(maxWidth, srcWidth);
    const newHeight = newWidth / aspectRatio;

    if (newHeight > maxHeight) {
      const adjustedHeight = maxHeight;
      const adjustedWidth = adjustedHeight * aspectRatio;
      return { width: adjustedWidth, height: adjustedHeight };
    }

    return { width: newWidth, height: newHeight };
  };


  const handleMouseDown = (event: React.MouseEvent<HTMLCanvasElement>) => {
    setDrawing(true);
    const { offsetX, offsetY } = event.nativeEvent;
    setStartPoint({ x: offsetX, y: offsetY });
  };

  const handleMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!drawing) return;

    const { offsetX, offsetY } = event.nativeEvent;
    const boundingBox = calculateBoundingBox(startPoint.x, startPoint.y, offsetX, offsetY);
    // const width = offsetX - startPoint.x;
    // const height = offsetY - startPoint.y;
    drawWithBox(boundingBox);
  };

  const handleMouseUp = (event: React.MouseEvent<HTMLCanvasElement>) => {
    setDrawing(false);
    const { offsetX, offsetY } = event.nativeEvent;
    const box = calculateBoundingBox(
      startPoint.x,
      startPoint.y,
      offsetX, 
      offsetY
    );
    // console.log("NEW BOX!");

    const canvas = canvasRef.current;
    if (canvas && image) {
      // console.log("image: ", image.width, image.height);
      // console.log("canvas: ", canvas.width, canvas.height);
      
      const widthMult = image.width / canvas.width;
      const heightMult = image.height / canvas.height;

      const drawnBox = {
        x1: Math.floor(Math.min(startPoint.x, offsetX) * widthMult),
        y1: Math.floor(Math.min(startPoint.y, offsetY) * heightMult),
        x2: Math.floor(Math.max(startPoint.x, offsetX) * widthMult),
        y2: Math.floor(Math.max(startPoint.y, offsetY) * heightMult),
      }
      // console.log(drawnBox);
      setDrawnBox(drawnBox);
    }

    drawWithBox(box);
  };

  const calculateBoundingBox = (startX: number, startY: number, endX: number, endY: number): BoundingBox => {
    const x = Math.min(startX, endX);
    const y = Math.min(startY, endY);
    const width = Math.abs(startX - endX);
    const height = Math.abs(startY - endY);

    return { x, y, width, height };
  };

  return (
    <Box
      style={{position: "relative"}}
    >
      <ImageUI
        src={imageSrc as string}
        alt="uploaded"
        style={{ maxWidth: "100%", maxHeight: "300px", pointerEvents: "none", userSelect: "none"}}
      />
      <canvas
        style={{ position: 'absolute', top: 0, left: 0 }}
        ref={canvasRef}
        width="500"
        height="300"
        // style={{ border: '1px solid black' }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseOut={() => setDrawing(false)}
      />
    </Box>
  );
};

export default ImageViewer;