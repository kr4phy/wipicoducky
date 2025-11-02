# IR 리모컨 디버그 모드 - 원시 신호 분석
# 각 버튼의 실제 신호를 캡처하여 코드 테이블을 만드는 도구
import board
import pulseio
import time
import adafruit_irremote

# 핀 설정
try:
    receiver = pulseio.PulseIn(board.GP17, maxlen=200, idle_state=True)
except ValueError as e:
    print(f"Error: {e}")
    import gc
    gc.collect()
    time.sleep(0.5)
    receiver = pulseio.PulseIn(board.GP17, maxlen=200, idle_state=True)

# 원본 펄스 데이터와 디코드된 코드 저장
decoder = adafruit_irremote.NonblockingGenericDecode(receiver)

print("=" * 60)
print("IR Remote Debugger - Raw Signal Analyzer")
print("=" * 60)
print("\n각 버튼을 누르고 결과를 기록하세요:")
print("(예: 0번, 1번, 2번, ..., +, -, PLAY/PAUSE 등)")
print("\nQuit하려면 Ctrl+C를 누르세요.\n")

signal_log = {}
signal_count = 0

try:
    while True:
        for message in decoder.read():
            try:
                # IRMessage인 경우
                if isinstance(message, adafruit_irremote.IRMessage):
                    code = message.code
                    pulses = message.pulses
                    signal_count += 1
                    
                    print(f"\n--- Signal #{signal_count} ---")
                    print(f"Pulses count: {len(pulses)}")
                    print(f"Pulses (first 20): {pulses[:20]}")
                    
                    # 디코드 결과
                    if isinstance(code, (list, tuple)) and len(code) >= 2:
                        addr, cmd = code[0], code[1]
                        print(f"Address: 0x{addr:02X}")
                        print(f"Command: 0x{cmd:02X}")
                        
                        # 신호 로그에 저장
                        key = f"cmd_0x{cmd:02X}"
                        if key not in signal_log:
                            signal_log[key] = {
                                'addr': addr,
                                'cmd': cmd,
                                'pulses': pulses,
                                'count': 1
                            }
                        else:
                            signal_log[key]['count'] += 1
                    
                    print("\n버튼을 누르세요:")
                
                # NECRepeatIRMessage인 경우 (무시)
                elif isinstance(message, adafruit_irremote.NECRepeatIRMessage):
                    pass
                
            except Exception as e:
                print(f"Error: {type(e).__name__}: {e}")
        
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n" + "=" * 60)
    print("수집된 신호 요약:")
    print("=" * 60)
    
    # 정렬된 결과 출력
    sorted_signals = sorted(signal_log.items(), key=lambda x: x[1]['cmd'])
    
    for key, data in sorted_signals:
        print(f"\n{key}:")
        print(f"  Address: 0x{data['addr']:02X}")
        print(f"  Command: 0x{data['cmd']:02X}")
        print(f"  수신 횟수: {data['count']}")
    
    print("\n" + "=" * 60)
    print("Python 코드로 변환:")
    print("=" * 60)
    print("\nkey_map = {")
    for key, data in sorted_signals:
        print(f"    0x{data['cmd']:02X}: \"버튼_이름\",  # 주소: 0x{data['addr']:02X}")
    print("}")
    
    print("\n" + "=" * 60)
    print("종료합니다.")
    try:
        receiver.deinit()
    except:
        pass
