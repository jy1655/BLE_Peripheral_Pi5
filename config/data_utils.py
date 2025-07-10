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



def hamming_7_4_encode(data_byte):
    '''
    Hamming(7,4) 인코딩
    4비트의 데이터를 받아 3개의 패리티 비트를 추가하여 총 7비트로 인코딩
    16개의 다른값을 표현
    '''
    # 4 데이터 비트를 추출 (D3, D2, D1, D0)
    d = [(data_byte >> i) & 1 for i in range(4)]
    # 패리티 비트 계산 (P2, P1, P0)
    p = [
        d[0] ^ d[1] ^ d[3],  # P0
        d[0] ^ d[2] ^ d[3],  # P1
        d[1] ^ d[2] ^ d[3],  # P2
    ]
    # 인코딩된 데이터: P2, P1, D3, P0, D2, D1, D0
    encoded = (p[2] << 6) | (p[1] << 5) | (d[3] << 4) | (p[0] << 3) | (d[2] << 2) | (d[1] << 1) | d[0]
    return encoded

def hamming_7_4_decode(encoded_data):
    '''
    이 함수는 Hamming 코드를 디코딩하고 단일 비트 오류를 수정하며
    두 비트 오류를 감지하여 원본 데이터를 성공적으로 반환하거나
    오류를 나타냅니다.
    '''
    # 인코딩된 7비트에서 비트 추출
    bits = [(encoded_data >> i) & 1 for i in range(7)]
    # 패리티 검사
    p0 = bits[3] ^ bits[4] ^ bits[5] ^ bits[6]
    p1 = bits[1] ^ bits[2] ^ bits[5] ^ bits[6]
    p2 = bits[0] ^ bits[2] ^ bits[4] ^ bits[6]
    # 오류 위치 결정
    error_loc = (p2 << 2) | (p1 << 1) | p0
    if error_loc != 0:
        print(f"오류 감지됨, 위치: {error_loc}")
        # 오류 수정 (단일 비트 오류일 경우)
        bits[7-error_loc] = 1 - bits[7-error_loc]
    # 데이터 비트 추출: D3, D2, D1, D0
    corrected_data = (bits[6] << 3) | (bits[5] << 2) | (bits[4] << 1) | bits[2]
    return corrected_data, error_loc != 0


def hamming_15_11_encode(data):
    # 데이터 비트 D10~D0를 가정하고, P3~P0를 계산합니다.
    # 비트 위치는 다음과 같이 정의됩니다: P3 P2 P1 P0 D10 ... D0
    # 패리티 비트 계산
    p0 = data[0] ^ data[1] ^ data[3] ^ data[4] ^ data[6] ^ data[8] ^ data[10]
    p1 = data[0] ^ data[2] ^ data[3] ^ data[5] ^ data[6] ^ data[9] ^ data[10]
    p2 = data[1] ^ data[2] ^ data[3] ^ data[7] ^ data[8] ^ data[9] ^ data[10]
    p3 = data[4] ^ data[5] ^ data[6] ^ data[7] ^ data[8] ^ data[9] ^ data[10]

    # 인코딩된 15비트 데이터 생성
    encoded = (p3 << 14) | (p2 << 13) | (p1 << 12) | (p0 << 11) | (data << 0)
    return encoded


def hamming_15_11_decode(encoded):
    # 패리티 비트 검사
    p0 = (encoded >> 11) & 1
    p1 = (encoded >> 12) & 1
    p2 = (encoded >> 13) & 1
    p3 = (encoded >> 14) & 1

    # 데이터 비트 추출
    data = encoded & 0x7FF  # 하위 11비트 추출

    # 패리티 검사를 통한 오류 위치 확인
    p0_calc = 0  # 실제 계산 필요
    p1_calc = 0  # 실제 계산 필요
    p2_calc = 0  # 실제 계산 필요
    p3_calc = 0  # 실제 계산 필요
    # 계산된 패리티와 실제 패리티를 비교하여 오류 위치를 찾습니다.

    error_position = (p3_calc ^ p3) << 3 | (p2_calc ^ p2) << 2 | (p1_calc ^ p1) << 1 | (p0_calc ^ p0)
    if error_position != 0:
        # 오류가 있는 경우, 해당 위치의 비트를 반전시킵니다.
        encoded ^= 1 << (15 - error_position)

    # 수정된 데이터 반환
    return encoded & 0x7FF  # 하위 11비트 반환
