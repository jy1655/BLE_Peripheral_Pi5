#include "BLEService.h"
#include "BLECharacteristic.h"
#include <iostream>

static const gchar introspection_xml[] =
    "<node>"
    "  <interface name='org.bluez.GattService1'>"
    "    <property name='UUID' type='s' access='read'/>"
    "    <property name='Primary' type='b' access='read'/>"
    "    <property name='Characteristics' type='ao' access='read'/>"
    "  </interface>"
    "</node>";

BLEService::BLEService(const std::string& uuid, bool primary) 
    : m_uuid(uuid), m_primary(primary), m_connection(nullptr), m_registrationId(0) {
}

BLEService::~BLEService() {
    unregisterService();
}

void BLEService::addCharacteristic(std::shared_ptr<BLECharacteristic> characteristic) {
    m_characteristics.push_back(characteristic);
}

bool BLEService::registerService(GDBusConnection* connection) {
    m_connection = connection;
    
    GError* error = nullptr;
    GDBusNodeInfo* introspection_data = g_dbus_node_info_new_for_xml(introspection_xml, &error);
    
    if (error) {
        std::cerr << "Failed to parse introspection XML: " << error->message << std::endl;
        g_error_free(error);
        return false;
    }
    
    std::string object_path = "/org/bluez/example/service" + std::to_string(reinterpret_cast<uintptr_t>(this));
    
    GDBusInterfaceVTable interface_vtable = {
        handleMethodCall,
        nullptr, // get_property
        nullptr  // set_property
    };
    
    m_registrationId = g_dbus_connection_register_object(connection,
                                                        object_path.c_str(),
                                                        introspection_data->interfaces[0],
                                                        &interface_vtable,
                                                        this,
                                                        nullptr,
                                                        &error);
    
    g_dbus_node_info_unref(introspection_data);
    
    if (error) {
        std::cerr << "Failed to register service object: " << error->message << std::endl;
        g_error_free(error);
        return false;
    }
    
    // Register characteristics
    for (auto& characteristic : m_characteristics) {
        if (!characteristic->registerCharacteristic(connection, object_path)) {
            std::cerr << "Failed to register characteristic: " << characteristic->getUUID() << std::endl;
        }
    }
    
    std::cout << "Service registered: " << m_uuid << " at " << object_path << std::endl;
    return true;
}

void BLEService::unregisterService() {
    if (m_connection && m_registrationId > 0) {
        g_dbus_connection_unregister_object(m_connection, m_registrationId);
        m_registrationId = 0;
    }
    
    for (auto& characteristic : m_characteristics) {
        characteristic->unregisterCharacteristic();
    }
}

void BLEService::handleMethodCall(GDBusConnection* connection,
                                 const gchar* sender,
                                 const gchar* object_path,
                                 const gchar* interface_name,
                                 const gchar* method_name,
                                 GVariant* parameters,
                                 GDBusMethodInvocation* invocation,
                                 gpointer user_data) {
    // Handle method calls for GattService1 interface
    std::cout << "Method call: " << method_name << std::endl;
}