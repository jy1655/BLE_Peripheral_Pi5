#ifndef BLE_CHARACTERISTIC_H
#define BLE_CHARACTERISTIC_H

#include <string>
#include <vector>
#include <functional>
#include <cstdint>
#include <gio/gio.h>

class BLECharacteristic {
public:
    enum Flags {
        FLAG_READ = 0x01,
        FLAG_WRITE = 0x02,
        FLAG_NOTIFY = 0x04,
        FLAG_INDICATE = 0x08
    };

    using ReadCallback = std::function<std::vector<uint8_t>()>;
    using WriteCallback = std::function<void(const std::vector<uint8_t>&)>;

    BLECharacteristic(const std::string& uuid, uint32_t flags);
    ~BLECharacteristic();

    void setReadCallback(ReadCallback callback);
    void setWriteCallback(WriteCallback callback);
    void setValue(const std::vector<uint8_t>& value);
    void notifyValue(const std::vector<uint8_t>& value);
    
    bool registerCharacteristic(GDBusConnection* connection, const std::string& servicePath);
    void unregisterCharacteristic();
    
    const std::string& getUUID() const { return m_uuid; }
    uint32_t getFlags() const { return m_flags; }

private:
    std::string m_uuid;
    uint32_t m_flags;
    std::vector<uint8_t> m_value;
    ReadCallback m_readCallback;
    WriteCallback m_writeCallback;
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

#endif // BLE_CHARACTERISTIC_H