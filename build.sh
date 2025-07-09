#!/bin/bash

# Build script for BLE Peripheral Pi5 project

echo "Building BLE Peripheral for Raspberry Pi 5..."

# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake .. || { echo "CMake configuration failed"; exit 1; }

# Build the project
make -j$(nproc) || { echo "Build failed"; exit 1; }

echo "Build completed successfully!"
echo "Run with: sudo ./BLE_Peripheral_Pi5"