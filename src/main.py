from gi.repository import GLib
import sys
from dbus import SystemBus
from dbus.mainloop.glib import DBusGMainLoop
from ble_manager import BLEManager
import ble_auto_confirm
import argparse

"""
메인 함수: BLE 광고 및 GATT 서비스 등록을 관리합니다.

매개변수:
- timeout (int): 광고를 진행할 시간(초)입니다. 0이면 무한히 실행합니다.
"""
def main(timeout=0):
    # D-Bus 메인 루프를 GLib 이벤트 루프와 통합합니다.
    DBusGMainLoop(set_as_default=True)
    bus = SystemBus()  # 시스템 버스에 연결합니다.
    mainloop = GLib.MainLoop()  # GLib 메인 루프를 생성합니다.

    # BLE 페어링 요청을 자동으로 처리하는 에이전트를 등록합니다.
    ble_auto_confirm.register_agent(bus)

    # BLE 매니저를 초기화합니다.
    ble_manager = BLEManager(bus, mainloop)

    # GATT 서비스를 설정하고 등록합니다.
    print("GATT 서비스 등록을 시작합니다...")
    ble_manager.registering_gatt()

    # BLE 광고를 시작하여 디바이스를 발견 가능하게 합니다.
    print("BLE 광고를 시작합니다...")
    ble_manager.start_advertising()

    if timeout > 0:
        # 타임아웃이 지정된 경우, 지정된 시간 후에 메인 루프를 종료합니다.
        GLib.timeout_add_seconds(timeout, mainloop.quit)
    else:
        # 타임아웃이 지정되지 않은 경우, 무한히 광고를 진행합니다.
        print('무한히 광고를 진행합니다...')

    try:
        # GLib 메인 루프를 시작합니다.
        mainloop.run()
    except KeyboardInterrupt:
        # 키보드 인터럽트(Ctrl+C)를 처리하여 안전하게 종료합니다.
        print("사용자에 의해 중단되었습니다, 종료합니다...")
    finally:
        # 광고를 중지하고 자원을 정리합니다.
        ble_manager.stop_advertising()
        sys.exit(0)

if __name__ == "__main__":
    # 명령줄 인자를 파싱하여 광고 타임아웃을 설정합니다.
    parser = argparse.ArgumentParser(description="BLE 광고 스크립트")
    parser.add_argument(
        '--timeout',
        default=0,
        type=int,
        help=(
            "지정된 초 동안 광고를 진행한 후 중지합니다. "
            "0으로 설정하면 무한히 실행됩니다 (기본값: 0)."
        )
    )
    args = parser.parse_args()

    # 지정된 타임아웃으로 메인 함수를 실행합니다.
    main(args.timeout)
