# data_utils.py

"""
기기간 데이터 전송시에 필요한 데이터 타입 변환 기능들을 모아둔 스크립트
바이트 배열을 16진수 형태로 표현한거나
D-Bus 시스템의 데이터 타입을 Python의 기본 데이터 타입으로 변환하는 등의 기능들을 구현
"""

import dbus

def byteArrayToHexString(bytes):
    """
    바이트 배열을 16진수 형태로 표현
    """
    hex_string = ""
    for byte in bytes:
        hex_byte = '%02X' % byte # %02X 포맷을 사용하여 16진수로 변환 (필요할 경우 앞을 0으로 채운다는 것)
        hex_string = hex_string + hex_byte
    return hex_string


def dbus_to_python(data):
    """
    D-Bus 시스템에서 사용되는 다양한 데이터 타입을 Python의 기본 데이터 타입으로 변환
    """
    type_map = {
        dbus.String: str,
        dbus.ObjectPath: str,
        dbus.Boolean: bool,
        dbus.Int64: int,
        dbus.Int32: int,
        dbus.Int16: int,
        dbus.UInt16: int,
        dbus.Byte: int,
        dbus.Double: float
    }

    if type(data) in type_map:
        return type_map[type(data)](data)
    elif isinstance(data, dbus.Array):
        return [dbus_to_python(value) for value in data]
    elif isinstance(data, dbus.Dictionary):
        return {key: dbus_to_python(value) for key, value in data.items()}
    else:
        return 
    
    
def to_dbus_array(items, signature):
    """Python 리스트를 dbus.Array로 변환합니다."""
    return dbus.Array(items, signature=signature)

def to_dbus_dict(data, signature):
    """Python 사전을 dbus.Dictionary로 변환합니다."""
    return dbus.Dictionary(data, signature=signature)

def to_dbus_string(text):
    """Python 문자열을 dbus.String으로 변환합니다."""
    return dbus.String(text)
    

def text_to_ascii_array(text):
    """
    텍스트 문자열을 ASCII 값의 배열로 변환
    """
    ascii_value = []
    for character in text:
        ascii_value.append(ord(character))
    return ascii_value

"""
def print_properties(props):
    for key in props:
        print(key + "=" str(props[key]))
""" 
    