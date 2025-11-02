# IR 리모컨 -> HID 입력 (CircuitPython + adafruit_irremote + adafruit_hid)
# NonblockingGenericDecode를 사용한 버전 (권장: 더 견고함)
import board
import pulseio
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

# ducky.py 임포트
from ducky import runScript

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

# NonblockingGenericDecode를 사용하여 비블로킹 IR 신호 디코딩
decoder = adafruit_irremote.NonblockingGenericDecode(receiver)

# USB HID 키보드 초기화
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

irremote_payloads = [
    # 0번: 기본 명령 테스트
    "GUI\nSTRING cmd\nDELAY 200\nENTER\nDELAY 1500\nSTRING echo HELLO WORLD\nENTER\n",
    
    # 1번: 시스템 정보 조회
    "GUI\nSTRING cmd\nDELAY 200\nENTER\nDELAY 1500\nSTRING systeminfo | findstr /I OS\nENTER\n",
    
    # 2번: 현재 디렉토리 목록
    "GUI\nSTRING cmd\nDELAY 200\nENTER\nDELAY 1500\nSTRING dir\nENTER\n",
    
    # 3번: 네트워크 설정 확인
    "GUI\nSTRING cmd\nDELAY 200\nENTER\nDELAY 1500\nSTRING ipconfig\nENTER\n",
    
    # 4번: 파일 탐색기 열기
    "GUI\nSTRING cmd\nDELAY 200\nENTER\nDELAY 1500\nSTRING explorer C:\\\nENTER\n",
    
    # 5번: 작업 관리자 열기 (Ctrl+Shift+Esc 동시 입력)
    "CTRL SHIFT ESC\n",
    
    # 6번: 메모장 열기
    "GUI\nSTRING notepad\nDELAY 200\nENTER\n",
    
    # 7번: PowerShell 열기
    "GUI\nSTRING powershell\nDELAY 200\nENTER\n",
    
    # 8번: 디스크 용량 확인
    "GUI\nSTRING cmd\nDELAY 200\nENTER\nDELAY 1500\nSTRING wmic logicaldisk get size,freespace,name\nENTER\n",
    
    # 9번: 프로세스 목록 확인
    "ALT F4\n",
]

def decodeKeyValue(data):
    """IR 리모컨의 신호를 확인 (공식 정의)
    
    NEC 프로토콜의 확장 형식 (4개 요소):
    code = (address, ~address, command, ~command)
    이 함수는 command 부분(data)을 받아서 처리합니다.
    """
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
    return "UNKNOWN"

print("IR -> HID ready (NonblockingGenericDecode mode)")
print("NEC 확장 형식 지원 (4개 요소): (address, ~address, command, ~command)")
print()

try:
    while True:
        # 수신한 모든 메시지 처리
        for message in decoder.read():
            try:
                # IRMessage인 경우: 정상적으로 디코된 메시지
                if isinstance(message, adafruit_irremote.IRMessage):
                    code = message.code
                    pulses = message.pulses
                    
                    # NEC 코드 처리 (4개 요소 또는 2개 요소)
                    if isinstance(code, (list, tuple)):
                        if len(code) == 4:
                            # 확장 NEC 형식: (addr, ~addr, cmd, ~cmd)
                            addr, addr_inv, cmd, cmd_inv = code[0], code[1], code[2], code[3]
                            key = decodeKeyValue(cmd)
                            
                            # 디버깅 정보 출력
                            print("[NEW] addr: 0x%02X cmd: 0x%02X => %s (pulses: %d)" % (addr, cmd, key, len(pulses)))
                            
                            # 숫자 0-9 입력 시 해당 스크립트 실행
                            if key in "0123456789":
                                script_index = int(key)
                                if script_index < len(irremote_payloads):
                                    print(f"[SCRIPT] Executing payload #{script_index}...")
                                    try:
                                        runScript(irremote_payloads[script_index])
                                    except Exception as e:
                                        print(f"[ERROR] Script execution failed: {e}")
                                else:
                                    print(f"[ERROR] Payload #{script_index} not found")
                            # '+' 또는 '-' 수신 시 HID로 해당 문자 전송
                            elif key == "+":
                                layout.write("+")
                            elif key == "-":
                                layout.write("-")
                        
                        elif len(code) >= 2:
                            # 표준 형식: (addr, cmd)
                            addr, cmd = code[0], code[1]
                            key = decodeKeyValue(cmd)
                            
                            print("[NEW] addr: 0x%02X cmd: 0x%02X => %s (pulses: %d)" % (addr, cmd, key, len(pulses)))
                            
                            # 숫자 0-9 입력 시 해당 스크립트 실행
                            if key in "0123456789":
                                script_index = int(key)
                                if script_index < len(irremote_payloads):
                                    print(f"[SCRIPT] Executing payload #{script_index}...")
                                    try:
                                        runScript(irremote_payloads[script_index])
                                    except Exception as e:
                                        print(f"[ERROR] Script execution failed: {e}")
                                else:
                                    print(f"[ERROR] Payload #{script_index} not found")
                            # '+' 또는 '-' 수신 시 HID로 해당 문자 전송
                            elif key == "+":
                                layout.write("+")
                            elif key == "-":
                                layout.write("-")
                
                # NECRepeatIRMessage인 경우: 반복 신호 (무시)
                elif isinstance(message, adafruit_irremote.NECRepeatIRMessage):
                    pass  # 반복 신호는 무시
                
                # UnparseableIRMessage인 경우: 파싱 실패 (무시)
                else:
                    pass
            
            except Exception as e:
                print("Error processing message:", type(e).__name__, e)
        
        # CPU 사용률 낮추기
        time.sleep(0.01)

except KeyboardInterrupt:
    try:
        receiver.deinit()
    except Exception:
        pass
    print("IR -> HID stopped")

