#ifndef BLE_PERIPHERAL_H
#define BLE_PERIPHERAL_H

#include <string>
#include <vector>
#include <memory>
#include <gio/gio.h>

class BLEService;
class BLEAdvertisement;

class BLEPeripheral {
public:
    BLEPeripheral(const std::string& name);
    ~BLEPeripheral();

    bool initialize();
    void start();
    void stop();
    void addService(std::shared_ptr<BLEService> service);
    bool startAdvertising();
    void stopAdvertising();

private:
    std::string m_name;
    GDBusConnection* m_connection;
    std::vector<std::shared_ptr<BLEService>> m_services;
    std::unique_ptr<BLEAdvertisement> m_advertisement;
    bool m_running;
    
    static void onBusAcquired(GDBusConnection* connection, const gchar* name, gpointer user_data);
    static void onNameAcquired(GDBusConnection* connection, const gchar* name, gpointer user_data);
    static void onNameLost(GDBusConnection* connection, const gchar* name, gpointer user_data);
};

#endif // BLE_PERIPHERAL_H