#gatt_manager.py

"""
org.bluez.GattManager1 에 정의될 Gatt 데이터 세부 정의 

메소드: ble_gatt.py에서 정의
데이터: advertisement_config.py에 정의(미완성-하드코딩된 부분 존재)
"""

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # config 폴더를 절대경로로 가져오기 위한 코드

from config import advertising_config, data_utils
import dbus
import ble_gatt
import random
from gi.repository import GLib



def find_adapter(bus):
    """
    Searches for a BLE adapter that supports GATT services.
    """
    remote_om = dbus.Interface(bus.get_object(advertising_config.BLUEZ_SERVICE, '/'),
                               advertising_config.DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if advertising_config.GATT_MANAGER_IFACE in props.keys():
            return o
        
    print("No object in path")
    return None



def gatt_service_manager(bus):
    """
    Retrieves the GATT service manager from the BLE adapter.
    """
    adapter = find_adapter(bus)
    if not adapter:
        print('GattManager1 interface not found')
        return

    service_manager = dbus.Interface(
            bus.get_object(advertising_config.BLUEZ_SERVICE, adapter),
            advertising_config.GATT_MANAGER_IFACE)
    
    return service_manager


def gatt_app(bus):
    """
    Initializes and returns a GATT application with a GattServices.
    여기에서 service를 추가하여야 실제로 광고에 포함됨
    """
    app = ble_gatt.GattApplication(bus)

    app.add_service(TemperatureService(bus, 0))
    # app.add_service(new_service(bus,1))

    return app



# Example Gatt service and characteristic
class TemperatureService(ble_gatt.GattService):
    def __init__(self, bus, index):
        ble_gatt.GattService.__init__(self, bus, index,
                                      advertising_config.TEMPERATURE_SVC_UUID, True
        )
        print("Adding TemperatureCharacteristic to the service")
        self.add_characteristic(TemperatureCharacteristic(bus, 0, self))
        self.add_characteristic(LedTextCharacteristic(bus, 1, self))


class TemperatureCharacteristic(ble_gatt.GattCharacteristic):
    temperature = 0
    delta = 0
    notifying = False

    def __init__(self, bus, index, service):
        ble_gatt.GattCharacteristic.__init__(
            self, bus, index, advertising_config.TEMPERATURE_CHR_UUID,
            ['read', 'notify'], service
        )
        self.notifying = False
        self.temperature = random.randint(0,50)
        print("initial temperature set to" + str(self.temperature))
        self.delta = 0
        GLib.timeout_add(1000, self.simulate_temperature)

    def simulate_temperature(self):
        self.delta = random.randint(-1, 1)
        self.temperature = self.temperature + self.delta
        if (self.temperature > 50):
            self.temperature = 50
        elif (self.temperature < 0):
            self.temperature = 0
        print("simulated temperature: "+ str(self.temperature)+ "C")
        if self.notifying: 
            self.notify_temperature()
        GLib.timeout_add(1000, self.simulate_temperature)

    def notify_temperature(self):
        value = []
        value.append(dbus.Byte(self.temperature))
        print("noty temp = " + str(self.temperature))
        self.PropertiesChanged(advertising_config.GATT_CHRC_IFACE, {"Value": value}, [])
        return self.notifying
    
    def StartNotify(self):
        print("start noty")
        self.notifying = True
    
    def StopNotify(self):
        print("stop noty")
        self.notifying = False


class LedTextCharacteristic(ble_gatt.GattCharacteristic):
    text = ""

    def __init__(self, bus, index, service):
        ble_gatt.GattCharacteristic.__init__(
            self, bus, index, advertising_config.LED_TEXT_CHR_UUID,
            ['write'], service
        )

    @dbus.service.method(advertising_config.GATT_CHRC_IFACE, in_signature='aya{sv}', out_signature='')
    def WriteValue(self, value, options):
        ascii_bytes = data_utils.dbus_to_python(value)
        self.text = ''.join([chr(byte) for byte in ascii_bytes])
        print(f"Received text: {self.text}")
        print(f"ascii code: {str(ascii_bytes)}")









    """
class HeartRateService(GattService):
    """
    #Fake Heart Rate Service that simulates a fake heart beat and control point
    #behavior.

    """
    HR_UUID = '0000180d-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index):
        GattService.__init__(self, bus, index, self.HR_UUID, True)
        self.add_characteristic(HeartRateMeasurementChrc(bus, 0, self))
        self.add_characteristic(BodySensorLocationChrc(bus, 1, self))
        self.add_characteristic(HeartRateControlPointChrc(bus, 2, self))
        self.energy_expended = 0


class HeartRateMeasurementChrc(GattCharacteristic):
    HR_MSRMT_UUID = '00002a37-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.HR_MSRMT_UUID,
                ['notify'],
                service)
        self.notifying = False
        self.hr_ee_count = 0

    def hr_msrmt_cb(self):
        value = []
        value.append(dbus.Byte(0x06))

        value.append(dbus.Byte(randint(90, 130)))

        if self.hr_ee_count % 10 == 0:
            value[0] = dbus.Byte(value[0] | 0x08)
            value.append(dbus.Byte(self.service.energy_expended & 0xff))
            value.append(dbus.Byte((self.service.energy_expended >> 8) & 0xff))

        self.service.energy_expended = \
                min(0xffff, self.service.energy_expended + 1)
        self.hr_ee_count += 1

        print('Updating value: ' + repr(value))

        self.PropertiesChanged(advertising_config.GATT_CHRC_IFACE, { 'Value': value }, [])

        return self.notifying

    def _update_hr_msrmt_simulation(self):
        print('Update HR Measurement Simulation')

        if not self.notifying:
            return

        GObject.timeout_add(1000, self.hr_msrmt_cb)

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self._update_hr_msrmt_simulation()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_hr_msrmt_simulation()


class BodySensorLocationChrc(GattCharacteristic):
    BODY_SNSR_LOC_UUID = '00002a38-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.BODY_SNSR_LOC_UUID,
                ['read'],
                service)

    def ReadValue(self, options):
        # Return 'Chest' as the sensor location.
        return [ 0x01 ]

class HeartRateControlPointChrc(GattCharacteristic):
    HR_CTRL_PT_UUID = '00002a39-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.HR_CTRL_PT_UUID,
                ['write'],
                service)

    def WriteValue(self, value, options):
        print('Heart Rate Control Point WriteValue called')

        if len(value) != 1:
            raise InvalidValueLengthException()

        byte = value[0]
        print('Control Point value: ' + repr(byte))

        if byte != 1:
            raise FailedException("0x80")

        print('Energy Expended field reset!')
        self.service.energy_expended = 0


class BatteryService(GattService):
    """
    #Fake Battery service that emulates a draining battery.

    """
    BATTERY_UUID = '180f'

    def __init__(self, bus, index):
        GattService.__init__(self, bus, index, self.BATTERY_UUID, True)
        self.add_characteristic(BatteryLevelCharacteristic(bus, 0, self))


class BatteryLevelCharacteristic(GattCharacteristic):
    """
    #Fake Battery Level characteristic. The battery level is drained by 2 points
    #every 5 seconds.

    """
    BATTERY_LVL_UUID = '2a19'

    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.BATTERY_LVL_UUID,
                ['read', 'notify'],
                service)
        self.notifying = False
        self.battery_lvl = 100
        GObject.timeout_add(5000, self.drain_battery)

    def notify_battery_level(self):
        if not self.notifying:
            return
        self.PropertiesChanged(
                advertising_config.GATT_CHRC_IFACE,
                { 'Value': [dbus.Byte(self.battery_lvl)] }, [])

    def drain_battery(self):
        if not self.notifying:
            return True
        if self.battery_lvl > 0:
            self.battery_lvl -= 2
            if self.battery_lvl < 0:
                self.battery_lvl = 0
        print('Battery Level drained: ' + repr(self.battery_lvl))
        self.notify_battery_level()
        return True

    def ReadValue(self, options):
        print('Battery Level read: ' + repr(self.battery_lvl))
        return [dbus.Byte(self.battery_lvl)]

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self.notify_battery_level()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False


class TestService(GattService):
    """
    #Dummy test service that provides characteristics and descriptors that
    #exercise various API functionality.

    """
    TEST_SVC_UUID = '12345678-1234-5678-1234-56789abcdef0'

    def __init__(self, bus, index):
        GattService.__init__(self, bus, index, self.TEST_SVC_UUID, True)
        self.add_characteristic(TestCharacteristic(bus, 0, self))
        self.add_characteristic(TestEncryptCharacteristic(bus, 1, self))
        self.add_characteristic(TestSecureCharacteristic(bus, 2, self))

class TestCharacteristic(GattCharacteristic):
    """
    #Dummy test characteristic. Allows writing arbitrary bytes to its value, and
    #contains "extended properties", as well as a test descriptor.

    """
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef1'

    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['read', 'write', 'writable-auxiliaries'],
                service)
        self.value = []
        self.add_descriptor(TestDescriptor(bus, 0, self))
        self.add_descriptor(
                GattCharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        print('TestCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('TestCharacteristic Write: ' + repr(value))
        self.value = value


class TestDescriptor(GattDescriptor):
    """
    #Dummy test descriptor. Returns a static value.

    """
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef2'

    def __init__(self, bus, index, characteristic):
        GattDescriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self, options):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]


class GattCharacteristicUserDescriptionDescriptor(GattDescriptor):
    """
    #Writable CUD descriptor.

    """
    CUD_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        self.writable = 'writable-auxiliaries' in characteristic.flags
        self.value = array.array('B', b'This is a characteristic for testing')
        self.value = self.value.tolist()
        GattDescriptor.__init__(
                self, bus, index,
                self.CUD_UUID,
                ['read', 'write'],
                characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise NotPermittedException()
        self.value = value

class TestEncryptCharacteristic(GattCharacteristic):
    """
    #Dummy test characteristic requiring encryption.

    """
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef3'

    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['encrypt-read', 'encrypt-write'],
                service)
        self.value = []
        self.add_descriptor(TestEncryptDescriptor(bus, 2, self))
        self.add_descriptor(
                GattCharacteristicUserDescriptionDescriptor(bus, 3, self))

    def ReadValue(self, options):
        print('TestEncryptCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('TestEncryptCharacteristic Write: ' + repr(value))
        self.value = value

class TestEncryptDescriptor(GattDescriptor):
    
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef4'

    def __init__(self, bus, index, characteristic):
        GattDescriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['encrypt-read', 'encrypt-write'],
                characteristic)

    def ReadValue(self, options):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]


class TestSecureCharacteristic(GattCharacteristic):
    
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef5'

    def __init__(self, bus, index, service):
        GattCharacteristic.__init__(
                self, bus, index,
                self.TEST_CHRC_UUID,
                ['secure-read', 'secure-write'],
                service)
        self.value = []
        self.add_descriptor(TestSecureDescriptor(bus, 2, self))
        self.add_descriptor(
                GattCharacteristicUserDescriptionDescriptor(bus, 3, self))

    def ReadValue(self, options):
        print('TestSecureCharacteristic Read: ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('TestSecureCharacteristic Write: ' + repr(value))
        self.value = value


class TestSecureDescriptor(GattDescriptor):
    
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef6'

    def __init__(self, bus, index, characteristic):
        GattDescriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['secure-read', 'secure-write'],
                characteristic)

    def ReadValue(self, options):
        return [
                dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]

"""