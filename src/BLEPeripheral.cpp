#include "BLEPeripheral.h"
#include "BLEService.h"
#include "BLEAdvertisement.h"
#include <iostream>
#include <thread>
#include <chrono>

BLEPeripheral::BLEPeripheral(const std::string& name) 
    : m_name(name), m_connection(nullptr), m_running(false) {
    m_advertisement = std::make_unique<BLEAdvertisement>(name);
}

BLEPeripheral::~BLEPeripheral() {
    stop();
}

bool BLEPeripheral::initialize() {
    GError* error = nullptr;
    
    // Connect to system bus first
    m_connection = g_bus_get_sync(G_BUS_TYPE_SYSTEM, nullptr, &error);
    if (error) {
        std::cerr << "Failed to connect to system bus: " << error->message << std::endl;
        g_error_free(error);
        return false;
    }
    
    if (!m_connection) {
        std::cerr << "Failed to get system bus connection" << std::endl;
        return false;
    }
    
    std::cout << "Connected to system bus" << std::endl;
    return true;
}

void BLEPeripheral::start() {
    if (m_running) return;
    
    std::cout << "Starting BLE Peripheral: " << m_name << std::endl;
    
    // Register services
    for (auto& service : m_services) {
        if (!service->registerService(m_connection)) {
            std::cerr << "Failed to register service: " << service->getUUID() << std::endl;
        }
    }
    
    // Give services time to register
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    // Start advertising after services are registered
    std::cout << "Note: BLE advertising via BlueZ manager may not work on this system." << std::endl;
    std::cout << "Services are registered and device is discoverable via 'bluetoothctl discoverable on'" << std::endl;
    
    // Try to start advertising, but don't fail if it doesn't work
    if (startAdvertising()) {
        std::cout << "BLE advertising started successfully" << std::endl;
    } else {
        std::cout << "BLE advertising failed - device is still connectable when discoverable" << std::endl;
    }
    
    m_running = true;
    
    // Start main loop
    GMainLoop* loop = g_main_loop_new(nullptr, FALSE);
    g_main_loop_run(loop);
    g_main_loop_unref(loop);
}

void BLEPeripheral::stop() {
    if (!m_running) return;
    
    std::cout << "Stopping BLE Peripheral" << std::endl;
    
    stopAdvertising();
    
    for (auto& service : m_services) {
        service->unregisterService();
    }
    
    m_running = false;
}

void BLEPeripheral::addService(std::shared_ptr<BLEService> service) {
    m_services.push_back(service);
    m_advertisement->addServiceUUID(service->getUUID());
}

bool BLEPeripheral::startAdvertising() {
    if (m_connection && m_advertisement) {
        return m_advertisement->start(m_connection);
    }
    return false;
}

void BLEPeripheral::stopAdvertising() {
    if (m_advertisement) {
        m_advertisement->stop();
    }
}

void BLEPeripheral::onBusAcquired(GDBusConnection* connection, const gchar* name, gpointer user_data) {
    std::cout << "Bus acquired: " << name << std::endl;
}

void BLEPeripheral::onNameAcquired(GDBusConnection* connection, const gchar* name, gpointer user_data) {
    std::cout << "Name acquired: " << name << std::endl;
}

void BLEPeripheral::onNameLost(GDBusConnection* connection, const gchar* name, gpointer user_data) {
    std::cout << "Name lost: " << name << std::endl;
}