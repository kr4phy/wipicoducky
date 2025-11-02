# IR 리모컨 -> HID 입력 (CircuitPython + adafruit_irremote + adafruit_hid)
import board
import pulseio
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

# adafruit_irremote 라이브러리 로드
try:
    import adafruit_irremote
except ImportError:
    print("ERROR: adafruit_irremote 라이브러리를 찾을 수 없습니다.")
    print("설치 방법: adafruit-circuitpython-irremote를 lib/ 폴더에 복사하세요.")
    raise

# 핀 설정
try:
    receiver = pulseio.PulseIn(board.GP17, maxlen=200, idle_state=True)
except ValueError as e:
    # GP17이 이미 사용 중인 경우, 기존 객체 초기화
    print(f"Warning: {e}")
    print("Attempting to reset GP17...")
    try:
        # 메모리 정리
        import gc
        gc.collect()
        time.sleep(0.5)
        receiver = pulseio.PulseIn(board.GP17, maxlen=200, idle_state=True)
    except Exception as e2:
        print(f"ERROR: GP17을 초기화할 수 없습니다: {e2}")
        print("해결 방법:")
        print("1. Pico W를 재시작하세요 (REPL 종료 후 재연결)")
        print("2. boot.py 또는 code.py에서 다른 프로그램이 GP17을 사용하는지 확인하세요")
        raise

# GenericDecode를 사용하여 IR 신호 디코딩
decoder = adafruit_irremote.GenericDecode()

# USB HID 키보드 초기화
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

def decodeKeyValue(data):
    if data == 0x68:
        return "0"
    if data == 0x30:
        return "1"
    if data == 0x18:
        return "2"
    if data == 0x7A:
        return "3"
    if data == 0x10:
        return "4"
    if data == 0x38:
        return "5"
    if data == 0x5A:
        return "6"
    if data == 0x42:
        return "7"
    if data == 0x4A:
        return "8"
    if data == 0x52:
        return "9"
    if data == 0x90:
        return "EQ"
    if data == 0xA8:
        return "+"
    if data == 0xE0:
        return "-"
    if data == 0xB0:
        return "200+"
    if data == 0x98:
        return "100+"
    if data == 0x22:
        return "PREV"
    if data == 0xC2:
        return "PLAY/PAUSE"
    if data == 0x02:
        return "NEXT"
    if data == 0xA2:
        return "CH-"
    if data == 0xE2:
        return "CH+"
    if data == 0x62:
        return "POWER"
    return "ERROR"

print("IR -> HID ready (blocking mode)")
print("NEC 확장 형식 지원 (4개 요소): (address, ~address, command, ~command)")
print()

try:
    while True:
        # read_pulses()를 사용하여 IR 신호 수집
        pulses = decoder.read_pulses(receiver, blocking=True, max_pulse=10000)
        
        if pulses is None:
            continue
        
        try:
            # decode_bits()를 사용하여 IR 신호 디코딩
            code = adafruit_irremote.decode_bits(pulses)
            
            if code:
                # NEC 코드 처리 (4개 요소 또는 2개 요소)
                if len(code) == 4:
                    # 확장 NEC 형식: (addr, ~addr, cmd, ~cmd)
                    addr, addr_inv, cmd, cmd_inv = code[0], code[1], code[2], code[3]
                elif len(code) >= 2:
                    # 표준 형식: (addr, cmd)
                    addr, cmd = code[0], code[1]
                else:
                    addr, cmd = None, code[0] if code else None
                
                if cmd is not None:
                    key = decodeKeyValue(cmd)
                    print("addr: 0x%02X cmd: 0x%02X" % (addr if addr else 0, cmd), "=>", key)
                    
                    # '+' 또는 '-' 수신 시 HID로 해당 문자 전송
                    if key == "+":
                        layout.write("+")
                    elif key == "-":
                        layout.write("-")
        
        except adafruit_irremote.IRNECRepeatException:
            # NEC 반복 신호는 무시
            print("NEC repeat signal")
            pass
        
        except adafruit_irremote.FailedToDecode as e:
            # 디코드 실패 메시지 확인
            print("Failed to decode:", e)
            pass
        
        except adafruit_irremote.IRDecodeException as e:
            # IR 디코드 예외 처리
            print("IR decode error:", e)
            pass
        
        except Exception as e:
            # 기타 예외 처리
            print("Error:", type(e).__name__, e)

except KeyboardInterrupt:
    try:
        receiver.deinit()
    except Exception:
        pass
