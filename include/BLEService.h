#ifndef BLE_SERVICE_H
#define BLE_SERVICE_H

#include <string>
#include <vector>
#include <memory>
#include <gio/gio.h>

class BLECharacteristic;

class BLEService {
public:
    BLEService(const std::string& uuid, bool primary = true);
    ~BLEService();

    void addCharacteristic(std::shared_ptr<BLECharacteristic> characteristic);
    bool registerService(GDBusConnection* connection);
    void unregisterService();
    
    const std::string& getUUID() const { return m_uuid; }
    bool isPrimary() const { return m_primary; }
    const std::vector<std::shared_ptr<BLECharacteristic>>& getCharacteristics() const { return m_characteristics; }

private:
    std::string m_uuid;
    bool m_primary;
    std::vector<std::shared_ptr<BLECharacteristic>> m_characteristics;
    GDBusConnection* m_connection;
    guint m_registrationId;
    
    static void handleMethodCall(GDBusConnection* connection,
                                const gchar* sender,
                                const gchar* object_path,
                                const gchar* interface_name,
                                const gchar* method_name,
                                GVariant* parameters,
                                GDBusMethodInvocation* invocation,
                                gpointer user_data);
};

#endif // BLE_SERVICE_H