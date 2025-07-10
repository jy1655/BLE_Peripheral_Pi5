# ble_auto_confirm.py

"""
BLE 광고중에 Central에서 연결 요청시 자동으로 연결될 수 있도록 하는 메소드

원래 Central에서 연결 요청시 Peripheral쪽에서 승인을 하여 서로 페어링 되는 과정이 필요함
Peripheral 승인 과정을 org.bluez.Agent1 인터페이스를 구현하여 BLE 장치의 연결 및 페어링 과정에서 사용자 승인 없이 자동으로 인증을 처리하도록 하는 클래스
"""


import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) # config 폴더를 절대경로로 가져오기 위한 코드
from config import advertising_config

import dbus
import dbus.service


AGENT_PATH = advertising_config.PATH_BASE + '/agent'

class AutoConfirmAgent(dbus.service.Object):
    """
    블루투스 연결 시 패스키 입력 과정을 자동화하기 위한 에이전트 클래스.
    'org.bluez.Agent1' 인터페이스를 구현함.
    """
    exit_on_release = True

    def set_exit_on_release(self, exit_on_release):
        # 에이전트가 해제될 때 프로그램을 종료할지 여부를 설정
        self.exit_on_release = exit_on_release

    @dbus.service.method(advertising_config.AGENT_IFACE, in_signature='', out_signature='')
    def Release(self):
        print("Agent released")
        if self.exit_on_release:
            # GLib.MainLoop().quit()
            print("exit plz")
            return

    @dbus.service.method(advertising_config.AGENT_IFACE, in_signature='os', out_signature='')
    def AuthorizeService(self, device, uuid):
        # 서비스 접근 권한 부여 요청 시 호출됨
        print(f"Authorized Service {device} UUID {uuid}")
        return

    @dbus.service.method(advertising_config.AGENT_IFACE, in_signature='o', out_signature='s')
    def RequestPinCode(self, device):
        # PIN 코드 요청 시 호출됨
        print(f"RequestPinCode {device}")
        return '0000'

    @dbus.service.method(advertising_config.AGENT_IFACE, in_signature='ou', out_signature='')
    def RequestConfirmation(self, device, passkey):
        # 패스키 확인 요청 시 호출됨
        print(f"Auto-confirming passkey {passkey} for device {device}")
        return

    @dbus.service.method(advertising_config.AGENT_IFACE, in_signature='o', out_signature='u')
    def RequestPasskey(self, device):
        # 패스키 요청 시 호출됨
        print(f"RequestPasskey {device}")
        return dbus.UInt32(0)


def register_agent(bus):
    # DBus 시스템 버스에 에이전트를 등록하고 기본 에이전트로 설정
    agent = AutoConfirmAgent(bus, AGENT_PATH)

    obj = bus.get_object(advertising_config.BLUEZ_SERVICE, '/org/bluez')
    mgr = dbus.Interface(obj, advertising_config.AGENT_MANAGER_IFACE)
    mgr.RegisterAgent(AGENT_PATH, 'KeyboardDisplay') # 에이전트 등록
    mgr.RequestDefaultAgent(AGENT_PATH) # 기본 에이전트로 설정

    print("Auto-confirming agent registered")
