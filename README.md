# BLE Peripheral on Raspberry Pi 5 (Ubuntu 24.04 LTS) with Python

This project creates a Bluetooth Low Energy (BLE) Peripheral application using Python on a Raspberry Pi 5 running Ubuntu 24.04 LTS. It enables communication with mobile applications (iOS/Android) and other BLE-enabled devices through a custom GATT service.

## Features

- ✅ Advertise custom BLE services and characteristics
- ✅ Send and receive data over BLE
- ✅ GATT service with read/write characteristics
- ✅ Compatible with iOS and Android devices
- ✅ D-Bus integration with BlueZ stack
- ✅ Basic example implementation for demonstration

## System Requirements

- **Hardware**: Raspberry Pi 5 with built-in Bluetooth
- **OS**: Ubuntu 24.04 LTS
- **Python**: 3.12.3 or compatible version
- **BlueZ**: 5.66 or newer with experimental features enabled
- **Permissions**: User must be in `bluetooth` group

## Setup and Installation

### 1. System Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Bluetooth and development tools
sudo apt install bluetooth bluez bluez-tools python3-pip python3-dev python3-gi python3-gi-dev -y

# Install Python dependencies
pip install -r requirements.txt
```

### 2. User Permissions

```bash
# Add user to bluetooth group
sudo usermod -a -G bluetooth $USER

# Reboot to apply group changes
sudo reboot
```

### 3. BlueZ Configuration

**Enable experimental features for BLE peripheral support:**

```bash
# Edit BlueZ configuration
sudo nano /etc/bluetooth/main.conf
```

Add or uncomment these lines in the `[General]` section:
```ini
[General]
EnableExperimental = true
DbusExperimental = true
```

**Configure systemd service:**

```bash
# Create systemd override directory
sudo mkdir -p /etc/systemd/system/bluetooth.service.d/

# Create override configuration
sudo tee /etc/systemd/system/bluetooth.service.d/override.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=/usr/sbin/bluetoothd -n -d --experimental
EOF

# Reload systemd and restart bluetooth
sudo systemctl daemon-reload
sudo systemctl restart bluetooth
```

### 4. Verify Installation

```bash
# Check Bluetooth service status
sudo systemctl status bluetooth

# Verify experimental features are enabled
sudo bluetoothctl show | grep -i experimental

# Test Python dependencies
python3 -c "import dbus; from gi.repository import GLib; print('Dependencies OK')"
```

## Usage

### 1. Start the BLE Peripheral

```bash
# Navigate to project directory
cd /home/pi5test/Developments/BLE_Peripheral_Pi5_Python

# Run the BLE peripheral application
python3 main.py
```

**Expected output:**
```
Application registered.
Advertisement registered.
BLE Peripheral running. Press Ctrl+C to exit.
```

### 2. Connect from Mobile Devices

#### iOS (LightBlue App)
1. Download "LightBlue" from App Store
2. Open the app and scan for devices
3. Look for device with custom service UUID: `12345678-1234-5678-1234-56789abcdef0`
4. Connect to the device
5. Navigate to the custom service
6. Read/Write to characteristic: `12345678-1234-5678-1234-56789abcdef1`

#### Android (BLE Scanner/nRF Connect)
1. Download "BLE Scanner" or "nRF Connect" from Play Store
2. Ensure Location is enabled (required for BLE scanning)
3. Scan for BLE devices
4. Connect to the Raspberry Pi device
5. Explore the custom service and characteristics

### 3. Testing Data Exchange

**Default characteristic value:** "Hello" (in bytes)

**To read data:**
- Use mobile app to read characteristic value
- Should return: `[0x48, 0x65, 0x6C, 0x6C, 0x6F]` ("Hello")

**To write data:**
- Use mobile app to write new byte array to characteristic
- Check terminal output for received data

### 4. Stop the Application

```bash
# Press Ctrl+C to stop the application
# Clean shutdown will unregister advertisement and GATT services
```

## Project Structure

```
BLE_Peripheral_Pi5_Python/
├── main.py             # Main BLE Peripheral application
├── ble_service.py      # Additional service/characteristic classes
├── requirements.txt    # Python dependencies (dbus-python, PyGObject)
├── README.md           # Project documentation
└── venv/              # Virtual environment (optional)
```

## Service and Characteristic Details

### Custom Service
- **Service UUID**: `12345678-1234-5678-1234-56789abcdef0`
- **Type**: Primary service
- **Description**: Custom demonstration service

### Characteristic
- **Characteristic UUID**: `12345678-1234-5678-1234-56789abcdef1`
- **Properties**: Read, Write
- **Default Value**: "Hello" (ASCII bytes)
- **Description**: Basic read/write characteristic for data exchange

## Development Notes

### Current Implementation Status
- ✅ Basic BLE peripheral functionality
- ✅ GATT service and characteristic registration
- ✅ D-Bus integration with BlueZ
- ✅ Mobile device compatibility
- ⚠️ ObjectManager interface (recommended for production)
- ⚠️ Connection event handling
- ⚠️ Advanced error handling and logging

### Architecture
- **main.py**: Main application with complete BLE peripheral implementation
- **ble_service.py**: Auxiliary service/characteristic classes (currently unused)
- **requirements.txt**: Python dependencies

## Troubleshooting

### Common Issues

#### 1. Permission Denied Errors
```bash
# Solution: Add user to bluetooth group
sudo usermod -a -G bluetooth $USER
sudo reboot
```

#### 2. D-Bus Connection Failed
```bash
# Check if bluetooth service is running
sudo systemctl status bluetooth

# Restart bluetooth service
sudo systemctl restart bluetooth
```

#### 3. No Devices Found on Mobile
```bash
# Verify experimental features are enabled
sudo bluetoothctl show | grep -i experimental

# Check if advertisement is active
sudo bluetoothctl show | grep -i advertising
```

#### 4. Python Import Errors
```bash
# Install missing dependencies
pip install -r requirements.txt

# For system-wide installation
sudo apt install python3-gi python3-gi-dev
```

#### 5. BlueZ Version Issues
```bash
# Check BlueZ version (should be 5.66+)
bluetooth --version

# Update if necessary
sudo apt update && sudo apt upgrade bluez
```

### Debug Mode

```bash
# Run with verbose D-Bus logging
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus python3 main.py

# Check bluetoothd logs
sudo journalctl -u bluetooth -f
```

### Performance Optimization

- **Connection Interval**: Default settings work for most applications
- **Advertising Interval**: Currently using BlueZ defaults
- **MTU Size**: Negotiated automatically during connection

### Security Considerations

- Current implementation uses no authentication
- For production use, implement proper security measures
- Consider encryption and bonding for sensitive data

## Future Enhancements

- [ ] Connection event callbacks
- [ ] Multiple characteristics support
- [ ] Notification/indication support
- [ ] Advanced error handling
- [ ] Configuration file support
- [ ] Logging framework integration
- [ ] Unit tests
- [ ] Documentation generation

## Contributing

Feel free to submit issues and enhancement requests. When contributing:

1. Test on actual hardware (Raspberry Pi 5)
2. Verify mobile device compatibility
3. Follow existing code style
4. Update documentation as needed

