import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # config 폴더를 절대경로로 가져오기 위한 코드
from config import advertising_config

import ble_advertisement
import gatt_manager
import time

connected = 0
register_ble = None


class BLEManager:


    def __init__(self, bus, mainloop):
        self.bus = bus
        self.advertisement = None
        self.mainloop = mainloop
        


    def registering_gatt(self):

        # Create a new Gatt
        service_manager = gatt_manager.gatt_service_manager(self.bus)
        gatt_app = gatt_manager.gatt_app(self.bus)

        print('Registering GATT application...')

        service_manager.RegisterApplication(gatt_app.get_path(), {},
                                    reply_handler = self.register_app_cb,
                                    error_handler = self.register_app_error_cb)

        print("Start GATT")


    def start_advertising(self):

        global register_ble

        self.bus.add_signal_receiver(self.properties_changed,
                                     dbus_interface = advertising_config.DBUS_PROP_IFACE,
                                     signal_name = "PropertiesChanged",
                                     path_keyword = "path")
        
        self.bus.add_signal_receiver(self.interfaces_added,
                                     dbus_interface = advertising_config.DBUS_OM_IFACE,
                                     signal_name = "InterfacesAdded")

        # Create a new advertisement
        self.advertisement = ble_advertisement.LEAdvertisement(self.bus, 0)
        self.advertisement.add_manufacturer_data(0xffff, [0x00, 0x01, 0x02, 0x03])
        '''optional
        self.advertisement.add_service_uuid('180D')
        self.advertisement.add_service_uuid('180F')
        self.advertisement.add_manufacturer_data(0xffff, [0x00, 0x01, 0x02, 0x03])
        self.advertisement.add_service_data('9999', [0x00, 0x01, 0x02, 0x03, 0x04])
        self.advertisement.include_tx_power = False
        self.advertisement.add_data(0x26, [0x01, 0x01, 0x00])
        '''
        
        # Finish Registering advertisement
        register_ble = ble_advertisement.RegisterAdvertisement()
        ad_manager = register_ble.make_ad_manager(self.bus, self.advertisement)
        register_id = ad_manager.RegisterAdvertisement(self.advertisement.get_path(), {},
                                        reply_handler = self.register_ad_cb,
                                        error_handler = self.register_ad_error_cb)
        print("Advertisement registered")

        print("BLE Advertising started")


    def stop_advertising(self):

        global register_ble

        if self.advertisement:
            register_ble.unregister(self.advertisement)
        
            print("EXIT BLE Advertising")


    def stop_main_loop(self):
        if self.mainloop.is_running():
            self.mainloop.quit()


    def shutdown(self, timeout):
        print('Advertising for {} seconds...'.format(timeout))
        time.sleep(timeout)
        self.mainloop.quit()

    """
    def disconnect_all_devices(self):
        
        # 버스의 프로시 객체 관리자를 얻습니다.
        om = self.bus.get_object(advertising_config.BLUEZ_SERVICE, '/')
        managed_objects = om.GetManagedObjects()
        print(managed_objects)
        # 모든 관리 객체를 순회합니다.
        for path, interfaces in managed_objects.items():
            # Bluetooth 디바이스 인터페이스가 있는지 확인합니다.
            if advertising_config.DEVICE_IFACE in interfaces:
                device_props = interfaces[advertising_config.DEVICE_IFACE]
                if device_props.get("Connected", False):
                    print(f"{path}에 있는 디바이스가 연결되어 있습니다. 연결 해제 중...")
                
                    # 디바이스의 메소드를 호출하여 연결을 해제합니다.
                    device_obj = self.bus.get_object(advertising_config.BLUEZ_SERVICE, path)
                    try:
                        device_obj.Disconnect(reply_handler=self.on_device_disconnected, error_handler=self.on_device_disconnect_error)
                    except Exception as e:
                        print(f"{path}에 있는 디바이스를 해제하는 중 에러가 발생했습니다: {str(e)}")
            else:
                print("check code")
    """
    
    def set_connected_status(self, status):
        global connected
        if (status == 1):
            print("connected")
            connected = 1
            
        else:
            print("disconnected")
            connected = 0
            

    def properties_changed(self, interface, changed, invalidated, path):
        if (interface == advertising_config.DEVICE_IFACE):
            if ("Connected" in changed):
                self.set_connected_status(changed["Connected"])


    def interfaces_added(self, path, interfaces):
        if advertising_config.DEVICE_IFACE in interfaces:
            properties = interfaces[advertising_config.DEVICE_IFACE]
            if ("Connected" in properties):
                self.set_connected_status(properties["Connected"])


    def register_app_cb(self):
        print('GATT application registered')

    def register_app_error_cb(self, error):
        print('Failed to register application: ' + str(error))
        self.stop_main_loop(self.mainloop)

    def register_ad_cb(self):
        print('Advertisement registered')

    def register_ad_error_cb(self, error):
        print('Failed to register advertisement: ' + str(error))
        self.stop_main_loop(self.mainloop)

    def on_device_disconnected():
        print("Device disconnected successfully.")

    def on_device_disconnect_error(error):
        print(f"Failed to disconnect device: {str(error)}")