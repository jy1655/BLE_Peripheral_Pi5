# BLE Peripheral for Raspberry Pi 5

A C++ implementation of a Bluetooth Low Energy (BLE) peripheral for Raspberry Pi 5 using D-Bus and BlueZ.

## Features

- **BLE Peripheral Implementation**: Complete BLE peripheral using BlueZ D-Bus API
- **Custom Services**: Support for custom GATT services and characteristics
- **Read/Write/Notify**: Full support for BLE characteristic operations
- **Advertisement**: Configurable BLE advertising
- **Example Implementation**: Device Information Service and Custom Service examples

## Requirements

- Raspberry Pi 5 with Bluetooth support
- BlueZ 5.x
- CMake 3.16+
- GLib 2.0 development libraries
- D-Bus development libraries

## Build Instructions

1. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y libdbus-1-dev libglib2.0-dev cmake build-essential
   ```

2. **Build the Project**:
   ```bash
   mkdir build
   cd build
   cmake ..
   make
   ```

3. **Run the Application**:
   ```bash
   sudo ./BLE_Peripheral_Pi5
   ```

## Architecture

### Core Classes

- **BLEPeripheral**: Main peripheral manager
- **BLEService**: GATT service implementation
- **BLECharacteristic**: GATT characteristic with read/write/notify support
- **BLEAdvertisement**: BLE advertisement manager

### Example Services

1. **Device Information Service**: Provides device name and information
2. **Custom Service**: Example service with:
   - Read characteristic (returns "Hello from Pi5!")
   - Write characteristic (accepts data input)
   - Notify characteristic (sends periodic sensor data)

## Usage

The application creates a BLE peripheral that advertises as "Pi5-BLE-Device" and provides:

- Device name characteristic (read-only)
- Custom data characteristic (read-only)
- Write characteristic (accepts commands)
- Notification characteristic (sends periodic updates)

## Configuration

Edit `src/main.cpp` to customize:
- Device name and advertisement settings
- Service and characteristic UUIDs
- Callback functions for read/write operations
- Notification intervals and data

## Troubleshooting

- Ensure BlueZ is running: `sudo systemctl status bluetooth`
- Check Bluetooth adapter: `hciconfig`
- Run with elevated permissions (sudo) for D-Bus system bus access
- Verify no other BLE applications are using the adapter

## License

This project is provided as-is for educational and development purposes.