import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # config 폴더를 절대경로로 가져오기 위한 코드

from config import advertising_config, bluetooth_exceptions
import dbus
import dbus.service



class GattApplication(dbus.service.Object):
    """
    Implements the 'org.bluez.GattApplication1' interface for managing GATT services in a BLE application.
    Acts as a container for all GATT services offered by this application.
    """
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(advertising_config.DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        print('GetManagedObjects')

        for service in self.services:
            print("GetManagedObjects: service="+service.get_path())
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response
    


class GattService(dbus.service.Object):
    """
    Represents a GATT service. Implements 'org.bluez.GattService1'.
    A service groups functionality of a device, e.g., a temperature measurement service.
    """
    SERVICE_BASE = advertising_config.PATH_BASE + '/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.SERVICE_BASE + str(index)
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    @dbus.service.method(advertising_config.DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != advertising_config.GATT_SERVICE_IFACE:
            raise bluetooth_exceptions.InvalidArgsException()
        return self.get_properties()[advertising_config.GATT_SERVICE_IFACE]
        

    def get_properties(self):
        """
        Returns properties of the GATT service to be exposed over D-Bus.
        """
        return {
            advertising_config.GATT_SERVICE_IFACE: {
                'UUID': self.uuid,
                'Primary': self.primary,
                'Characteristics': dbus.Array(
                    self.get_characteristic_paths(),
                    signature='o')
            }
        }

    def get_path(self):
        # Returns the D-Bus object path of this service.
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic):
        # Adds a GATT characteristic to this service.
        self.characteristics.append(characteristic)

    def get_characteristic_paths(self):
        result = []
        for chrc in self.characteristics:
            result.append(chrc.get_path())
        return result

    def get_characteristics(self):
        # Returns all characteristics added to this service.
        return self.characteristics

    @dbus.service.method(advertising_config.DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != advertising_config.GATT_SERVICE_IFACE:
            raise bluetooth_exceptions.InvalidArgsException()

        return self.get_properties()[advertising_config.GATT_SERVICE_IFACE]


class GattCharacteristic(dbus.service.Object):
    """
    Represents a GATT characteristic. Implements org.bluez.GattCharacteristic1.
    Characteristics are the fundamental data points communicated between a BLE device and a client.
    """
    def __init__(self, bus, index, uuid, flags, service):
        self.path = service.path + '/char' + str(index)
        print('creating Characteristic with path='+self.path)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.descriptors = []
        """
        # D-Bus 신호 수신기 설정
        self.bus.add_signal_receiver(self.properties_changed,
                                     dbus_interface=advertising_config.DBUS_PROP_IFACE,
                                     signal_name="PropertiesChanged",
                                     path_keyword="path")
        """
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        # Returns properties of the GATT characteristic to be exposed over D-Bus.
        return {
                advertising_config.GATT_CHRC_IFACE: {
                        'Service': self.service.get_path(),
                        'UUID': self.uuid,
                        'Flags': self.flags,
                        'Descriptors': dbus.Array(
                                self.get_descriptor_paths(),
                                signature='o')
                }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_descriptor(self, descriptor):
        # Adds a GATT descriptor to this characteristic.
        self.descriptors.append(descriptor)

    def get_descriptor_paths(self):
        result = []
        for desc in self.descriptors:
            result.append(desc.get_path())
        return result

    def get_descriptors(self):
        # Returns all descriptors added to this characteristic
        return self.descriptors
    """   
    def properties_changed(self, interface, changed, invalidated, path=None):
    # 속성 변화를 처리하는 로직
        if interface == advertising_config.DEVICE_IFACE and "Connected" in changed:
            connected = changed["Connected"]

            if connected:
                print(f"{path}에서 장치가 연결되었습니다.")
            else:
                print(f"{path}에서 장치가 연결 해제되었습니다.")
                # 추가적인 연결 해제 처리 수행 가능
    """
    @dbus.service.method(advertising_config.DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != advertising_config.GATT_CHRC_IFACE:
            raise bluetooth_exceptions.InvalidArgsException()

        return self.get_properties()[advertising_config.GATT_CHRC_IFACE]

    @dbus.service.method(advertising_config.GATT_CHRC_IFACE, in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        print('Default ReadValue called, returning error')
        raise bluetooth_exceptions.NotSupportedException()

    @dbus.service.method(advertising_config.GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise bluetooth_exceptions.NotSupportedException()

    @dbus.service.method(advertising_config.GATT_CHRC_IFACE)
    def StartNotify(self):
        print('Default StartNotify called, returning error')
        raise bluetooth_exceptions.NotSupportedException()

    @dbus.service.method(advertising_config.GATT_CHRC_IFACE)
    def StopNotify(self):
        print('Default StopNotify called, returning error')
        raise bluetooth_exceptions.NotSupportedException()

    @dbus.service.signal(advertising_config.DBUS_PROP_IFACE, signature='sa{sv}as')
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class GattDescriptor(dbus.service.Object):
    """
    Represents a GATT descriptor. Implements 'org.bluez.GattDescriptor1'.
    Descriptors provide additional information and functionality to a characteristic.
    """
    def __init__(self, bus, index, uuid, flags, characteristic):
        self.path = characteristic.path + '/desc' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.flags = flags
        self.chrc = characteristic
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        # Returns properties of the GATT descriptor to be exposed over D-Bus.
        return {
            advertising_config.GATT_DESC_IFACE: {
                'Characteristic': self.chrc.get_path(),
                'UUID': self.uuid,
                'Flags': self.flags,
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)


    @dbus.service.method(advertising_config.DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != advertising_config.GATT_DESC_IFACE:
            raise bluetooth_exceptions.InvalidArgsException()

        return self.get_properties()[advertising_config.GATT_DESC_IFACE]


    @dbus.service.method(advertising_config.GATT_DESC_IFACE,
                        in_signature='a{sv}',
                        out_signature='ay')
    def ReadValue(self, options):
        print ('Default ReadValue called, returning error')
        raise bluetooth_exceptions.NotSupportedException()


    @dbus.service.method(advertising_config.GATT_DESC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        print('Default WriteValue called, returning error')
        raise bluetooth_exceptions.NotSupportedException()

