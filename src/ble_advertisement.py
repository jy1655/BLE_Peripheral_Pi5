import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # config 폴더를 절대경로로 가져오기 위한 코드
from config import advertising_config, bluetooth_exceptions
from config.data_utils import to_dbus_array, to_dbus_dict, to_dbus_string
import dbus
import dbus.service


class LEAdvertisement(dbus.service.Object):
    """
    This class represents a BLE advertisement.
    BlueZ 의 org.bluez.LEAdvertisement1 interface documentation:
    광고 데이터 정의
    """
    PATH_BASE = advertising_config.PATH_BASE + '/advertisement' # Unique path for this advertisement instance based on an index.

    def __init__(self, bus, index, advertising_type = 'peripheral'):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus # The DBus connection.
        self.ad_type = advertising_type # Type of advertisement. Usually, it's 'peripheral'.
        self.service_uuids = advertising_config.SERVICE_UUID # Default setup from the config. This can include UUIDs for services your device offers.
        self.manufacturer_data = None # For those sweet, sweet manufacturer-specific bytes.
        self.solicit_uuids = None # UUIDs this device is actively seeking.
        self.service_data = None # Additional data associated with a service UUID.
        self.local_name = advertising_config.DEVICE_NAME # The name that shows up in scans.
        self.include_tx_power = advertising_config.INCLUDE_TX_POWER # If we're shouting our power level.
        self.data = None # Generic data field for anything else you want to pack in.
        self.discoverable = True # Makes the device discoverable.
        dbus.service.Object.__init__(self, bus, self.path)


    def get_properties(self):
        """
        Packages all the advertisement properties into a DBus-friendly format.
        """
        properties = dict()
        properties['Type'] = self.ad_type
        if self.service_uuids is not None:
            properties['ServiceUUIDs'] = to_dbus_array(self.service_uuids, signature='s')

        if self.solicit_uuids is not None:
            properties['SolicitUUIDs'] = to_dbus_array(self.solicit_uuids, signature='s')

        if self.manufacturer_data is not None:
            properties['ManufacturerData'] = to_dbus_dict(self.manufacturer_data, signature='qv')
        
        if self.service_data is not None:
            properties['ServiceData'] = to_dbus_dict(self.service_data, signature='sv')
    
        if self.local_name is not None:
            properties['LocalName'] = to_dbus_string(self.local_name)
    
        if self.include_tx_power:
            properties['Includes'] = to_dbus_array(["tx-power"], signature='s')

        if self.data is not None:
            properties['Data'] = to_dbus_dict(self.data, signature='yv')

        return {advertising_config.LE_ADVERTISEMENT_IFACE: properties}


    def get_path(self):
        """
        Returns the DBus path for this advertisement object. 
        Essential for DBus to know where to find this.
        """
        return dbus.ObjectPath(self.path)
    

    # Add props
    def add_service_uuid(self, uuid):
        if not self.service_uuids:
            self.service_uuids = []
        self.service_uuids.append(uuid)

    def erase_service_uuid(self):
        self.service_uuids = advertising_config.SERVICE_UUID

    def add_solicit_uuid(self, uuid):
        if not self.solicit_uuids:
            self.solicit_uuids = []
        self.solicit_uuids.append(uuid)

    def erase_solicit_uuid(self):
        self.solicit_uuids = []

    def add_manufacturer_data(self, manuf_code, data):
        if not self.manufacturer_data:
            self.manufacturer_data = to_dbus_dict({}, signature='qv')
        self.manufacturer_data[manuf_code] = to_dbus_array(data, signature='y')

    def add_service_data(self, uuid, data):
        if not self.service_data:
            self.service_data = to_dbus_dict({}, signature='sv')
        self.service_data[uuid] = to_dbus_array(data, signature='y')

    def erase_service_data(self):
        self.service_data = to_dbus_dict({}, signature='sv')

    def add_data(self, ad_type, data):
        if not self.data:
            self.data = to_dbus_dict({}, signature='yv')
        self.data[ad_type] = to_dbus_array(data, signature='y')

    def erase_data(self):
        self.data = to_dbus_dict({}, signature='yv')


    @dbus.service.method(advertising_config.DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        """
        DBus method to get all properties for this advertisement.
        """
        print("GetAll")
        if interface != advertising_config.LE_ADVERTISEMENT_IFACE:
            raise bluetooth_exceptions.InvalidArgsException()
        print('returning props')
        return self.get_properties()[advertising_config.LE_ADVERTISEMENT_IFACE]


    @dbus.service.method(advertising_config.LE_ADVERTISEMENT_IFACE, in_signature='', out_signature='')
    def Release(self):
        """
        Clean up when this advertisement is no longer needed.
        """
        print('%s: Released!' % self.path)
        # 추가 코드 필요


    def find_adapter(self, bus):
        """
        Finds the BLE adapter to use for advertising. 
        Essential because we need to hook our advertisement onto an actual Bluetooth device.
        """
        remote_om = dbus.Interface(bus.get_object(advertising_config.BLUEZ_SERVICE, '/'),
                               advertising_config.DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()

        for o, props in objects.items():
            if advertising_config.LE_ADVERTISING_MANAGER_IFACE in props:
                return o

        print("No object in path")
        return None


class RegisterAdvertisement:
    """
    Handles the registration of an advertisement with the BlueZ backend.
    It's the bridge between your advertisement and the Bluetooth stack on the system.
    """
    def __init__(self):
        self.ad_manager = None

    
    def find_adapter(bus):
        """
        Finds the BLE adapter to use for advertising. 
        Essential because we need to hook our advertisement onto an actual Bluetooth device.
        """
        remote_om = dbus.Interface(bus.get_object(advertising_config.BLUEZ_SERVICE, '/'),
                               advertising_config.DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()

        for o, props in objects.items():
            if advertising_config.LE_ADVERTISING_MANAGER_IFACE in props:
                return o

        print("No object in path")
        return None


    def make_ad_manager(self, bus, advertisement):
        """
        Sets up everything needed to start advertising.
        """
        adapter = advertisement.find_adapter(bus)
        if not adapter:
            print("LEAdvevtisingManager1 interface not found")
            return

        adapter_props = dbus.Interface(bus.get_object(advertising_config.BLUEZ_SERVICE, adapter),
                                       advertising_config.DBUS_PROP_IFACE)
        adapter_props.Set(advertising_config.ADAPTER_IFACE, "Powered", dbus.Boolean(1))

        ad_manager_obj = bus.get_object(advertising_config.BLUEZ_SERVICE, adapter)

        self.ad_manager = dbus.Interface(ad_manager_obj, advertising_config.LE_ADVERTISING_MANAGER_IFACE)

        return self.ad_manager


    def unregister(self, advertisement):
        """
        Stops the advertisement and cleans up.
        """
        if self.ad_manager is None:
            print("Error: ad_manager is not initialized.")
            return
        
        self.ad_manager.UnregisterAdvertisement(advertisement)
        
        dbus.service.Object.remove_from_connection(advertisement)

        print("Advertisement unregistered")







