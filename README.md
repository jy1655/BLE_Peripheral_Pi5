# Oculo Bot BLE Peripheral on Ubuntu Python

우분투(리눅스) 기반 BLE peripheral advertisement 프로젝트.<br>
Ubuntu 22.04 기반에 BlueZ 라이브러리를 사용했고, BLE central 디바이스와의 문자열 통신을 전제함.
현재 버전에서는 Py-Dbus 라이브러리를 사용하여 Legacy Type의 광고만 가능함

<br>

## 1. Prerequisites

이 프로젝트를 빌드하고 실행하기 전 다음과 같은 것을 설치할 필요가 있음.
  1. python3
  2. dbus-python 1.3.2
  3. 기타 종속성 라이브러리

<br>

### 1.1. 블루투스 라이브러리 (BlueZ)
BlueZ 및 관련 개발 라이브러리 설치

```bash
sudo apt update
sudo apt install bluez libbluetooth-dev
```

<br>
~~
### 1.2. DBus - 

 `/etc/dbus-1/system.d/bluetooth.conf` 파일 일부 수정
```bash
  <policy user="root">
    <allow own="org.bluez"/>
    **<allow receive_sender="org.bluez"/>**
    <allow send_destination="org.bluez"/>
    <allow send_interface="org.bluez.AdvertisementMonitor1"/>
    <allow send_interface="org.bluez.Agent1"/>
    <allow send_interface="org.bluez.MediaEndpoint1"/>
    <allow send_interface="org.bluez.MediaPlayer1"/>
    <allow send_interface="org.bluez.Profile1"/>
    <allow send_interface="org.bluez.GattCharacteristic1"/>
    <allow send_interface="org.bluez.GattDescriptor1"/>
    <allow send_interface="org.bluez.LEAdvertisement1"/>
    <allow send_interface="org.freedesktop.DBus.ObjectManager"/>
    <allow send_interface="org.freedesktop.DBus.Properties"/>
    <allow send_interface="org.mpris.MediaPlayer2.Player"/>
  </policy>
```
~~

BlueZ를 Experimental 모드로 실행해야 정상적으로 Peripheral Advertisement가 가능함


<br>

## 2. 프로젝트 실행

- 터미널 입력

    `python3 -u "/home/aidall/Developments/Oculo_Bot_BLE_Peripheral_Python/src/main.py"`




## 3. 프로젝트 구조

```bash
Oclulo_Bot_BLE_Peripheral_Python/
├── config/
│   ├── advertising_config.py
│   ├── bluetooth_exceptions.py
│   └── data_utils.py
├── src/
│   ├── __init__.py
│   ├── ble_advertisement.py
│   ├── ble_auto_confirm.py  
│   ├── ble_gatt.py
│   ├── ble_manager.py
│   ├── gatt_manager.py
│   └── main.py
├── .gitignore
├── README.md
└── requirements.txt
```

BLE 광고의 세부설정을 세팅하는 파일 
<br>
  `advertising_config.py`,
  `ble_manager`,
  `gatt_manager`






## 4. 