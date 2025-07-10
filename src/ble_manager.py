#ble_manager.py

"""
org.bluez.advertisement1 에 정의될 광고 데이터 세부 정의 

메소드: ble_advertisement.py에서 정의
데이터: advertisement_config.py에서 정의(미완성-하드코딩된 부분 존재)
"""

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # config 폴더를 절대경로로 가져오기 위한 코드
from config import advertising_config
import ble_advertisement
import gatt_manager
import time

connected = 0 # 처음에 연결되지 않음 상태 설정(1=연결, 0=연결없음)
register_ble = None # 광고를 등록할 글로벌 변수 설정


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
        self.advertisement.add_manufacturer_data(advertising_config.EXAMPLE_MANUF_CODE, 
                                                 [0x00, 0x01, 0x02, 0x03]
                                                 )
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
        ad_manager.RegisterAdvertisement(self.advertisement.get_path(), {},
                                        reply_handler = self.register_ad_cb,
                                        error_handler = self.register_ad_error_cb)
        print("Advertisement registered")

        print("BLE Advertising started")


    def stop_advertising(self):
        # Stop advertising (unregister advertisement data)
        global register_ble

        if self.advertisement:
            register_ble.unregister(self.advertisement)
        
            print("EXIT BLE Advertising")


    def stop_main_loop(self):
        # Quit Main loop
        if self.mainloop.is_running():
            self.mainloop.quit()


    def shutdown(self, timeout):
        # Quit Main loop after {timeout} second.
        print('Advertising for {} seconds...'.format(timeout))
        time.sleep(timeout)
        self.mainloop.quit()


    def set_connected_status(self, status):
        # Switch connected status (1= connected, 0= disconnected)
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