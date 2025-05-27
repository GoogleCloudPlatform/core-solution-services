module.exports = {
    presets: [
      //'@babel/preset-env', // Handles modern JS features
      '@babel/preset-react', // Handles JSX and React-specific syntax
      '@babel/preset-typescript', // If you're using TypeScript
    ],
    plugins: [
      '@babel/plugin-transform-runtime', // Required for async/await handling
      "babel-plugin-transform-import-meta"  // Add this plugin to transform import.meta
    ],
  };