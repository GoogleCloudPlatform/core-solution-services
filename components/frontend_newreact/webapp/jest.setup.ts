import '@testing-library/jest-dom';
require('dotenv').config();

beforeAll(() => {
  // Mocking import.meta.env for Jest tests
  globalThis.importMeta = {
    env: {
      VITE_PUBLIC_API_ENDPOINT: 'your_default_api_endpoint', // Replace with your default value
      // You can add other environment variables here if needed
    }
  };
});

afterAll(() => {
  // Clean up the mock after all tests are done
  delete globalThis.importMeta;
});