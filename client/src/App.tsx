import React from 'react';
import ImageUploader from './ImageUploader';
import { Box, Heading } from '@chakra-ui/react';

const App: React.FC = () => {
  return (
    <Box
      maxW={1000}
      p = {4}
      mx="auto"
    >
      <Heading
        textAlign={"center"}
      >Efficient-ViT-Guard</Heading>
      <Box
        my={5}
        textAlign={"center"}
      >
        Welcome to Efficient-ViT-Guard. To get started, upload an image below!
      </Box>
      
      <ImageUploader />
    </Box>
  );
};

export default App;
