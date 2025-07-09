#include "BLECharacteristic.h"
#include <iostream>

static const gchar introspection_xml[] =
    "<node>"
    "  <interface name='org.bluez.GattCharacteristic1'>"
    "    <method name='ReadValue'>"
    "      <arg type='a{sv}' name='options' direction='in'/>"
    "      <arg type='ay' name='value' direction='out'/>"
    "    </method>"
    "    <method name='WriteValue'>"
    "      <arg type='ay' name='value' direction='in'/>"
    "      <arg type='a{sv}' name='options' direction='in'/>"
    "    </method>"
    "    <method name='StartNotify'>"
    "    </method>"
    "    <method name='StopNotify'>"
    "    </method>"
    "    <property name='UUID' type='s' access='read'/>"
    "    <property name='Service' type='o' access='read'/>"
    "    <property name='Value' type='ay' access='read'/>"
    "    <property name='Flags' type='as' access='read'/>"
    "  </interface>"
    "</node>";

BLECharacteristic::BLECharacteristic(const std::string& uuid, uint32_t flags)
    : m_uuid(uuid), m_flags(flags), m_connection(nullptr), m_registrationId(0) {
}

BLECharacteristic::~BLECharacteristic() {
    unregisterCharacteristic();
}

void BLECharacteristic::setReadCallback(ReadCallback callback) {
    m_readCallback = callback;
}

void BLECharacteristic::setWriteCallback(WriteCallback callback) {
    m_writeCallback = callback;
}

void BLECharacteristic::setValue(const std::vector<uint8_t>& value) {
    m_value = value;
}

void BLECharacteristic::notifyValue(const std::vector<uint8_t>& value) {
    if (!(m_flags & FLAG_NOTIFY)) return;
    
    setValue(value);
    // TODO: Implement actual notification to connected clients
    std::cout << "Notifying value change for characteristic: " << m_uuid << std::endl;
}

bool BLECharacteristic::registerCharacteristic(GDBusConnection* connection, const std::string& servicePath) {
    m_connection = connection;
    
    GError* error = nullptr;
    GDBusNodeInfo* introspection_data = g_dbus_node_info_new_for_xml(introspection_xml, &error);
    
    if (error) {
        std::cerr << "Failed to parse introspection XML: " << error->message << std::endl;
        g_error_free(error);
        return false;
    }
    
    std::string object_path = servicePath + "/char" + std::to_string(reinterpret_cast<uintptr_t>(this));
    
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
        std::cerr << "Failed to register characteristic object: " << error->message << std::endl;
        g_error_free(error);
        return false;
    }
    
    std::cout << "Characteristic registered: " << m_uuid << " at " << object_path << std::endl;
    return true;
}

void BLECharacteristic::unregisterCharacteristic() {
    if (m_connection && m_registrationId > 0) {
        g_dbus_connection_unregister_object(m_connection, m_registrationId);
        m_registrationId = 0;
    }
}

void BLECharacteristic::handleMethodCall(GDBusConnection* connection,
                                       const gchar* sender,
                                       const gchar* object_path,
                                       const gchar* interface_name,
                                       const gchar* method_name,
                                       GVariant* parameters,
                                       GDBusMethodInvocation* invocation,
                                       gpointer user_data) {
    BLECharacteristic* characteristic = static_cast<BLECharacteristic*>(user_data);
    
    if (g_strcmp0(method_name, "ReadValue") == 0) {
        std::vector<uint8_t> value;
        if (characteristic->m_readCallback) {
            value = characteristic->m_readCallback();
        } else {
            value = characteristic->m_value;
        }
        
        GVariant* byte_array = g_variant_new_fixed_array(G_VARIANT_TYPE_BYTE, 
                                                        value.data(), 
                                                        value.size(), 
                                                        sizeof(uint8_t));
        g_dbus_method_invocation_return_value(invocation, g_variant_new("(ay)", byte_array));
    }
    else if (g_strcmp0(method_name, "WriteValue") == 0) {
        GVariant* value_variant;
        GVariant* options_variant;
        g_variant_get(parameters, "(ay@a{sv})", &value_variant, &options_variant);
        
        gsize length;
        const uint8_t* data = static_cast<const uint8_t*>(g_variant_get_fixed_array(value_variant, &length, sizeof(uint8_t)));
        
        std::vector<uint8_t> value(data, data + length);
        
        if (characteristic->m_writeCallback) {
            characteristic->m_writeCallback(value);
        } else {
            characteristic->m_value = value;
        }
        
        g_variant_unref(value_variant);
        g_variant_unref(options_variant);
        g_dbus_method_invocation_return_value(invocation, nullptr);
    }
    else if (g_strcmp0(method_name, "StartNotify") == 0) {
        std::cout << "Start notifications for: " << characteristic->m_uuid << std::endl;
        g_dbus_method_invocation_return_value(invocation, nullptr);
    }
    else if (g_strcmp0(method_name, "StopNotify") == 0) {
        std::cout << "Stop notifications for: " << characteristic->m_uuid << std::endl;
        g_dbus_method_invocation_return_value(invocation, nullptr);
    }
}