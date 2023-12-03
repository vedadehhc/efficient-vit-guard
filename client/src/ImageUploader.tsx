import React, { useState } from "react";
import { Box, Button, Center, Input, VStack, Image } from "@chakra-ui/react";

const ImageUploader: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<
    string | ArrayBuffer | null
  >(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [blurredImage, setBlurredImage] = useState<string | ArrayBuffer | null>(
    null
  );

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

    const formdata = new FormData();
    formdata.append("file", selectedFile, "aug2.png");

    const requestOptions = {
      method: "POST",
      body: formdata,
      // redirect: 'follow'
    };

    fetch("http://127.0.0.1:5000/upload-image", requestOptions)
      .then(response => response.arrayBuffer())
      .then(buffer => {
        const blob = new Blob([ buffer ]);
        const url = URL.createObjectURL( blob );
        setBlurredImage(url);
      })
      .catch((error) => console.log("error", error));

    // setBlurredImage(selectedImage);
  };

  return (
    <VStack spacing={4} align="center">
      <Center>
        <Input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          display="none"
          id="imageInput"
        />
        <label htmlFor="imageInput">
          <Button as="span">Upload Image</Button>
        </label>
      </Center>

      {selectedImage && (
        <>
          <Box>
            {/* <h3>Image preview:</h3> */}
            <Image
              src={selectedImage as string}
              alt="Uploaded"
              style={{ maxWidth: "100%", maxHeight: "300px" }}
            />
          </Box>

          <Button as="span" onClick={blurFaces}>
            Blur faces
          </Button>
        </>
      )}

      {blurredImage && (
        <Box>
          {/* <h3>Image preview:</h3> */}
          <Image
            src={blurredImage as string}
            alt="Blurred"
            style={{ maxWidth: "100%", maxHeight: "300px" }}
          />
        </Box>
      )}
    </VStack>
  );
};

export default ImageUploader;
