#include "BLEAdvertisement.h"
#include <iostream>
#include <cstring>

static const gchar introspection_xml[] =
    "<node>"
    "  <interface name='org.bluez.LEAdvertisement1'>"
    "    <method name='Release'>"
    "    </method>"
    "    <property name='Type' type='s' access='read'/>"
    "    <property name='ServiceUUIDs' type='as' access='read'/>"
    "    <property name='LocalName' type='s' access='read'/>"
    "    <property name='ManufacturerData' type='a{qv}' access='read'/>"
    "    <property name='Includes' type='as' access='read'/>"
    "    <property name='Appearance' type='q' access='read'/>"
    "    <property name='Flags' type='ay' access='read'/>"
    "  </interface>"
    "</node>";

BLEAdvertisement::BLEAdvertisement(const std::string& name)
    : m_localName(name), m_manufacturerCompanyId(0), m_connection(nullptr), 
      m_registrationId(0), m_active(false) {
}

BLEAdvertisement::~BLEAdvertisement() {
    stop();
}

void BLEAdvertisement::setLocalName(const std::string& name) {
    m_localName = name;
}

void BLEAdvertisement::addServiceUUID(const std::string& uuid) {
    m_serviceUUIDs.push_back(uuid);
}

void BLEAdvertisement::setManufacturerData(uint16_t companyId, const std::vector<uint8_t>& data) {
    m_manufacturerCompanyId = companyId;
    m_manufacturerData = data;
}

bool BLEAdvertisement::start(GDBusConnection* connection) {
    if (m_active) return true;
    
    m_connection = connection;
    
    GError* error = nullptr;
    GDBusNodeInfo* introspection_data = g_dbus_node_info_new_for_xml(introspection_xml, &error);
    
    if (error) {
        std::cerr << "Failed to parse introspection XML: " << error->message << std::endl;
        g_error_free(error);
        return false;
    }
    
    std::string object_path = "/org/bluez/example/advertisement0";
    
    GDBusInterfaceVTable interface_vtable = {
        handleMethodCall,
        handleGetProperty,
        nullptr
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
        std::cerr << "Failed to register advertisement object: " << error->message << std::endl;
        g_error_free(error);
        return false;
    }
    
    // Call RegisterAdvertisement on BlueZ
    GVariantBuilder builder;
    g_variant_builder_init (&builder, G_VARIANT_TYPE ("a{sv}"));
    GVariant* options = g_variant_builder_end (&builder);

    GVariant* result = g_dbus_connection_call_sync(connection,
                                                  "org.bluez",
                                                  "/org/bluez/hci0",
                                                  "org.bluez.LEAdvertisingManager1",
                                                  "RegisterAdvertisement",
                                                  g_variant_new("(o@a{sv})", object_path.c_str(), options),
                                                  nullptr,
                                                  G_DBUS_CALL_FLAGS_NONE,
                                                  10000,
                                                  nullptr,
                                                  &error);
    
    if (error) {
        std::cerr << "Failed to register advertisement with BlueZ: " << error->message << std::endl;
        std::cerr << "Error domain: " << g_quark_to_string(error->domain) << ", Code: " << error->code << std::endl;
        g_error_free(error);
        return false;
    }
    
    if (result) {
        g_variant_unref(result);
    }
    
    m_active = true;
    std::cout << "Advertisement started: " << m_localName << std::endl;
    return true;
}

void BLEAdvertisement::stop() {
    if (!m_active) return;
    
    if (m_connection) {
        GError* error = nullptr;
        std::string object_path = "/org/bluez/example/advertisement0";
        
        GVariant* result = g_dbus_connection_call_sync(m_connection,
                                                      "org.bluez",
                                                      "/org/bluez/hci0",
                                                      "org.bluez.LEAdvertisingManager1",
                                                      "UnregisterAdvertisement",
                                                      g_variant_new("(o)", object_path.c_str()),
                                                      nullptr,
                                                      G_DBUS_CALL_FLAGS_NONE,
                                                      -1,
                                                      nullptr,
                                                      &error);
        
        if (error) {
            std::cerr << "Failed to unregister advertisement: " << error->message << std::endl;
            g_error_free(error);
        }
        
        if (result) {
            g_variant_unref(result);
        }
    }
    
    if (m_connection && m_registrationId > 0) {
        g_dbus_connection_unregister_object(m_connection, m_registrationId);
        m_registrationId = 0;
    }
    
    m_active = false;
    std::cout << "Advertisement stopped" << std::endl;
}

void BLEAdvertisement::handleMethodCall(GDBusConnection* connection,
                                       const gchar* sender,
                                       const gchar* object_path,
                                       const gchar* interface_name,
                                       const gchar* method_name,
                                       GVariant* parameters,
                                       GDBusMethodInvocation* invocation,
                                       gpointer user_data) {
    if (g_strcmp0(method_name, "Release") == 0) {
        std::cout << "Advertisement released" << std::endl;
        g_dbus_method_invocation_return_value(invocation, nullptr);
    }
}

GVariant* BLEAdvertisement::handleGetProperty(GDBusConnection* connection,
                                              const gchar* sender,
                                              const gchar* object_path,
                                              const gchar* interface_name,
                                              const gchar* property_name,
                                              GError** error,
                                              gpointer user_data) {
    BLEAdvertisement* adv = static_cast<BLEAdvertisement*>(user_data);
    
    if (g_strcmp0(property_name, "Type") == 0) {
        return g_variant_new_string("peripheral");
    } else if (g_strcmp0(property_name, "ServiceUUIDs") == 0) {
        GVariantBuilder builder;
        g_variant_builder_init(&builder, G_VARIANT_TYPE("as"));
        for (const auto& uuid : adv->m_serviceUUIDs) {
            g_variant_builder_add(&builder, "s", uuid.c_str());
        }
        return g_variant_builder_end(&builder);
    } else if (g_strcmp0(property_name, "LocalName") == 0) {
        return g_variant_new_string(adv->m_localName.c_str());
    } else if (g_strcmp0(property_name, "Includes") == 0) {
        GVariantBuilder builder;
        g_variant_builder_init(&builder, G_VARIANT_TYPE("as"));
        g_variant_builder_add(&builder, "s", "local-name");
        return g_variant_builder_end(&builder);
    } else if (g_strcmp0(property_name, "Appearance") == 0) {
        return g_variant_new_uint16(0); // 0 = Unknown
    } else if (g_strcmp0(property_name, "Flags") == 0) {
        GVariantBuilder builder;
        g_variant_builder_init(&builder, G_VARIANT_TYPE("ay"));
        g_variant_builder_add(&builder, "y", 0x06); // LE General Discoverable Mode, BR/EDR Not Supported
        return g_variant_builder_end(&builder);
    }
    
    return nullptr;
}
