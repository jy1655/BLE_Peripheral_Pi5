#!/usr/bin/env python3

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

# Set up the main loop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

BUS_NAME = 'org.bluez.test'
ADAPTER_IFACE = 'org.bluez.Adapter1'

# Define your custom service and characteristic UUIDs
SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef1'

class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/test/advertisement'

    def __init__(self, bus, index):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = 'peripheral'
        self.service_uuids = [SERVICE_UUID]
        self.local_name = 'Pi5-BLE-Test'
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            'Type': self.ad_type,
            'ServiceUUIDs': dbus.Array(self.service_uuids, signature='s'),
            'LocalName': self.local_name
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method('org.bluez.LEAdvertisement1', in_signature='', out_signature='')
    def Release(self):
        print(f'{self.path}: Released')

class Service(dbus.service.Object):
    PATH_BASE = '/org/bluez/test/service'

    def __init__(self, bus, index, uuid, primary):
        self.path = self.PATH_BASE + str(index)
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            'UUID': self.uuid,
            'Primary': self.primary,
            'Characteristics': dbus.Array(self.get_characteristic_paths(), signature='o')
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def get_characteristic_paths(self):
        result = []
        for char in self.characteristics:
            result.append(char.get_path())
        return result

class Characteristic(dbus.service.Object):
    PATH_BASE = '/org/bluez/test/characteristic'

    def __init__(self, bus, index, uuid, flags, service):
        self.path = self.PATH_BASE + str(index)
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.value = [dbus.Byte(ord('H')), dbus.Byte(ord('e')), dbus.Byte(ord('l')), dbus.Byte(ord('l')), dbus.Byte(ord('o'))]
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            'Service': self.service.get_path(),
            'UUID': self.uuid,
            'Flags': dbus.Array(self.flags, signature='s'),
            'Value': dbus.Array(self.value, signature='y')
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method('org.bluez.GattCharacteristic1', in_signature='a{sv}', out_signature='ay')
    def ReadValue(self, options):
        print(f'ReadValue called, returning {self.value}')
        return dbus.Array(self.value, signature='y')

    @dbus.service.method('org.bluez.GattCharacteristic1', in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        print(f'WriteValue called, value: {value}')
        self.value = value

    @dbus.service.method('org.bluez.GattCharacteristic1', in_signature='', out_signature='')
    def StartNotify(self):
        print('StartNotify called')

    @dbus.service.method('org.bluez.GattCharacteristic1', in_signature='', out_signature='')
    def StopNotify(self):
        print('StopNotify called')

    @dbus.service.method('org.bluez.GattCharacteristic1', in_signature='', out_signature='b')
    def IsNotifying(self):
        return dbus.Boolean(False)

class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/org/bluez/test/application0'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method('org.freedesktop.DBus.ObjectManager', in_signature='', out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        
        for service in self.services:
            service_path = service.get_path()
            response[service_path] = {
                'org.bluez.GattService1': service.get_properties()
            }
            
            for char in service.characteristics:
                char_path = char.get_path()
                response[char_path] = {
                    'org.bluez.GattCharacteristic1': char.get_properties()
                }
        
        return response

def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.freedesktop.DBus.ObjectManager')
    objects = remote_om.GetManagedObjects()
    
    for path, ifaces in objects.items():
        if 'org.bluez.Adapter1' in ifaces:
            return path
    return None

def main():
    bus = dbus.SystemBus()
    
    # Find adapter
    adapter_path = find_adapter(bus)
    if not adapter_path:
        print('No Bluetooth adapter found!')
        return
    
    print(f'Using adapter: {adapter_path}')
    
    app = None
    advertisement = None
    
    try:
        # Create application
        app = Application(bus)
        
        # Create service
        service = Service(bus, 0, SERVICE_UUID, True)
        app.services.append(service)
        
        # Create characteristic
        char = Characteristic(bus, 0, CHARACTERISTIC_UUID, ['read', 'write'], service)
        service.characteristics.append(char)
        
        print('Registering GATT application...')
        
        # Register application
        gatt_manager = dbus.Interface(bus.get_object('org.bluez', adapter_path), 'org.bluez.GattManager1')
        gatt_manager.RegisterApplication(app.get_path(), {}, timeout=60)
        print('Application registered.')
        
        # Create and register advertisement
        advertisement = Advertisement(bus, 0)
        print('Registering advertisement...')
        
        ad_manager = dbus.Interface(bus.get_object('org.bluez', adapter_path), 'org.bluez.LEAdvertisingManager1')
        ad_manager.RegisterAdvertisement(advertisement.get_path(), {}, timeout=60)
        print('Advertisement registered.')
        
        print('\\nBLE Peripheral running successfully!')
        print('Service UUID:', SERVICE_UUID)
        print('Characteristic UUID:', CHARACTERISTIC_UUID)
        print('Press Ctrl+C to exit.\\n')
        
        # Run main loop
        mainloop = GLib.MainLoop()
        mainloop.run()
        
    except KeyboardInterrupt:
        print('\\nShutting down...')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if advertisement:
            try:
                ad_manager = dbus.Interface(bus.get_object('org.bluez', adapter_path), 'org.bluez.LEAdvertisingManager1')
                ad_manager.UnregisterAdvertisement(advertisement.get_path())
                print('Advertisement unregistered.')
            except:
                pass
        
        if app:
            try:
                gatt_manager = dbus.Interface(bus.get_object('org.bluez', adapter_path), 'org.bluez.GattManager1')
                gatt_manager.UnregisterApplication(app.get_path())
                print('Application unregistered.')
            except:
                pass

if __name__ == '__main__':
    main()