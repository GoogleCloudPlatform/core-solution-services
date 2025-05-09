#!/bin/bash

# Build the app for production
echo "Building the app..."
npm run build

# Deploy the app with Firebase
echo "Deploying the app to Firebase..."
firebase deploy --only hosting --project $PROJECT_ID