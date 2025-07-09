#ifndef BLE_ADVERTISEMENT_H
#define BLE_ADVERTISEMENT_H

#include <string>
#include <vector>
#include <cstdint>
#include <gio/gio.h>

class BLEAdvertisement {
public:
    BLEAdvertisement(const std::string& name);
    ~BLEAdvertisement();

    void setLocalName(const std::string& name);
    void addServiceUUID(const std::string& uuid);
    void setManufacturerData(uint16_t companyId, const std::vector<uint8_t>& data);
    
    bool start(GDBusConnection* connection);
    void stop();

private:
    std::string m_localName;
    std::vector<std::string> m_serviceUUIDs;
    uint16_t m_manufacturerCompanyId;
    std::vector<uint8_t> m_manufacturerData;
    GDBusConnection* m_connection;
    guint m_registrationId;
    bool m_active;
    
    static void handleMethodCall(GDBusConnection* connection,
                                const gchar* sender,
                                const gchar* object_path,
                                const gchar* interface_name,
                                const gchar* method_name,
                                GVariant* parameters,
                                GDBusMethodInvocation* invocation,
                                gpointer user_data);

    static GVariant* handleGetProperty(GDBusConnection* connection,
                                       const gchar* sender,
                                       const gchar* object_path,
                                       const gchar* interface_name,
                                       const gchar* property_name,
                                       GError** error,
                                       gpointer user_data);
};

#endif // BLE_ADVERTISEMENT_H