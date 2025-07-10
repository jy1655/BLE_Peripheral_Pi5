# Advertiging configuration parameters for the BLE advertising using BlueZ


DEVICE_NAME = "Oculo_BLE_Advertiser"

BLUEZ_SERVICE = 'org.bluez'

PATH_BASE = '/org/bluez/oculo'
ADAPTER_PATH = '/org/bluez/hci0'

DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'

ADAPTER_IFACE = BLUEZ_SERVICE + ".Adapter1"
DEVICE_IFACE = BLUEZ_SERVICE + '.Device1'
GATT_MANAGER_IFACE = BLUEZ_SERVICE + '.GattManager1'
GATT_SERVICE_IFACE = BLUEZ_SERVICE + '.GattService1'
GATT_CHRC_IFACE = BLUEZ_SERVICE + '.GattCharacteristic1'
GATT_DESC_IFACE = BLUEZ_SERVICE + '.GattDescriptor1'
LE_ADVERTISING_MANAGER_IFACE = BLUEZ_SERVICE + '.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE = BLUEZ_SERVICE + '.LEAdvertisement1'
AGENT_IFACE = BLUEZ_SERVICE + '.Agent1'
AGENT_MANAGER_IFACE = BLUEZ_SERVICE + '.AgentManager1'



SERVICE_UUID = [
    '180D'
]

MANUFACTURER_DATA = {
    #optional
}

INCLUDE_TX_POWER = False



# Example UUID
TEMPERATURE_SVC_UUID = "e95d6100-251d-470a-a062-fa1922dfa9a8"
TEMPERATURE_CHR_UUID = "e95d9250-251d-470a-a062-fa1922dfa9a8"
LED_TEXT_CHR_UUID = "e95d93ee-251d-470a-a062-fa1922dfa9a8"


