import React, { useState } from "react";
import { Box, Button, Center, Input, HStack, VStack, Image, Spinner } from "@chakra-ui/react";
import ImageViewer, { DrawnBox, Size } from "./ImageViewer";

const ImageUploader: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<
    string | ArrayBuffer | null
  >(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [blurredImage, setBlurredImage] = useState<string | ArrayBuffer | null>(
    null
  );
  const [drawnBox, setDrawnBox] = useState<DrawnBox | null>(null);
  const [blurLoading, setBlurLoading] = useState<boolean>(false);
  const [size, setSize] = useState<Size>({width: 0, height: 0});

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      setBlurredImage(null);

      reader.onloadend = () => {
        setSelectedImage(reader.result);
      };

      reader.readAsDataURL(file);
    }
  };

  const blurFaces = () => {
    // call api ...
    if (!selectedFile) return;
    if (!drawnBox) return;

    const formdata = new FormData();
    formdata.append("file", selectedFile, "aug2.png");
    formdata.append("x_1", drawnBox.x1.toString());
    formdata.append("y_1", drawnBox.y1.toString());
    formdata.append("x_2", drawnBox.x2.toString());
    formdata.append("y_2", drawnBox.y2.toString());

    const requestOptions: RequestInit = {
      method: "POST",
      body: formdata,
      // redirect: 'follow'
    };

    setBlurLoading(true);

    fetch("http://127.0.0.1:5000/upload-image", requestOptions)
      .then(response => response.arrayBuffer())
      .then(buffer => {
        const blob = new Blob([ buffer ]);
        const url = URL.createObjectURL( blob );
        setBlurredImage(url);
        setBlurLoading(false);
      })
      .catch((error) => console.log("error", error));

    // setBlurredImage(selectedImage);
  };

  return (
    <>
    <Center>
      <Input
        type="file"
        accept="image/*"
        onChange={handleImageChange}
        display="none"
        id="imageInput"
      />
      <label htmlFor="imageInput">
        <Button as="span" mr={5}>Upload Image</Button>
      </label>
      {selectedImage && <Button onClick={blurFaces}>
        Blur faces
      </Button>}
    </Center>
    <HStack spacing={4} mt={10} align="center" justifyContent={"center"}>

      {selectedImage && (
        <VStack>
          <ImageViewer imageSrc={selectedImage as string} setDrawnBox={setDrawnBox} setSize={setSize}/>
        </VStack>
      )}

      <Center
        width={size.width}
        height={size.height}
      >
      {blurLoading ? <Spinner/> : 
          blurredImage && 
          <Image
            src={blurredImage as string}
            alt="Blurred"
            style={{ maxWidth: "100%", maxHeight: "300px" }}
          />}
      </Center>
    </HStack>
  </>
  );
};

export default ImageUploader;
