# advertising_config.py

# Advertiging configuration parameters for the BLE advertising using BlueZ
"""
광고 파라미터 데이터 정의 

ble_manager.py, gatt_manager.py에서 사용되는 광고 데이터 정의
"""

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

EXAMPLE_UUID = '180D'


MANUFACTURER_DATA = {
    #optional
}

EXAMPLE_MANUF_CODE = '0xffff'

INCLUDE_TX_POWER = False



# Example UUID
TEMPERATURE_SVC_UUID = "e95d6100-251d-470a-a062-fa1922dfa9a8"
TEMPERATURE_CHR_UUID = "e95d9250-251d-470a-a062-fa1922dfa9a8"
LED_TEXT_CHR_UUID = "e95d93ee-251d-470a-a062-fa1922dfa9a8"


