#!/bin/bash
set -e  # Exit on any error

# Check if firebase-tools is installed
if ! command -v firebase &> /dev/null; then
    echo "Firebase CLI not found. Installing firebase-tools..."
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    bash "$PROJECT_ROOT/utils/install_firebase.sh"
fi

# Check if emulators are already running
echo "Checking emulator status..."
if curl -s http://localhost:8080 > /dev/null && curl -s http://localhost:9199 > /dev/null; then
    echo "Emulators already running"
else
    echo "Starting Firebase emulators..."
    firebase emulators:start --only firestore,storage --project fake-project &

    # Wait for emulators to be ready
    echo "Waiting for emulators to start..."
    timeout=30
    while ! curl -s http://localhost:8080 > /dev/null && ! curl -s http://localhost:9199 > /dev/null; do
        if [ $timeout -le 0 ]; then
            echo "Timeout waiting for emulators to start"
            exit 1
        fi
        timeout=$((timeout - 1))
        sleep 1
    done
    echo "Emulators are ready!"
fi

# Run the tests
echo "Running tests..."
go test -v ./...