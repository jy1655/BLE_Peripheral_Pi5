#include "BLEPeripheral.h"
#include "BLEService.h"
#include "BLECharacteristic.h"
#include <iostream>
#include <thread>
#include <chrono>

// Example service UUIDs
const std::string DEVICE_INFO_SERVICE_UUID = "0000180A-0000-1000-8000-00805F9B34FB";

// Example characteristic UUIDs
const std::string DEVICE_NAME_CHAR_UUID = "00002A00-0000-1000-8000-00805F9B34FB";

int main() {
    std::cout << "Starting BLE Peripheral on Raspberry Pi 5..." << std::endl;

    // Create peripheral
    BLEPeripheral peripheral("Pi5-BLE-Device");

    // Create Device Information Service
    auto deviceInfoService = std::make_shared<BLEService>(DEVICE_INFO_SERVICE_UUID);

    // Device Name characteristic (read-only)
    auto deviceNameChar = std::make_shared<BLECharacteristic>(DEVICE_NAME_CHAR_UUID,
                                                             BLECharacteristic::FLAG_READ);
    deviceNameChar->setReadCallback([]() -> std::vector<uint8_t> {
        std::string name = "Raspberry Pi 5";
        return std::vector<uint8_t>(name.begin(), name.end());
    });
    deviceInfoService->addCharacteristic(deviceNameChar);

    // Add services to peripheral
    peripheral.addService(deviceInfoService);

    // Initialize and start peripheral
    if (!peripheral.initialize()) {
        std::cerr << "Failed to initialize BLE peripheral" << std::endl;
        return 1;
    }

    // Start the peripheral (this will block)
    peripheral.start();

    return 0;
}
