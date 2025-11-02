# IR 신호 직접 분석 - GenericDecode 사용
import board
import pulseio
import time
import adafruit_irremote

print("=" * 60)
print("IR Remote Debug - Direct Pulse Analysis")
print("=" * 60)
print("\n각 버튼을 눌러서 신호를 수집합니다.")
print("Ctrl+C로 종료합니다.\n")

# 핀 설정
try:
    receiver = pulseio.PulseIn(board.GP17, maxlen=200, idle_state=True)
except ValueError as e:
    print(f"Error: {e}")
    import gc
    gc.collect()
    time.sleep(0.5)
    receiver = pulseio.PulseIn(board.GP17, maxlen=200, idle_state=True)

decoder = adafruit_irremote.GenericDecode()

signal_count = 0
signal_map = {}

try:
    while True:
        # read_pulses는 신호가 들어올 때까지 대기
        pulses = decoder.read_pulses(receiver, blocking=True, max_pulse=10000)
        
        if pulses is None:
            continue
        
        signal_count += 1
        print(f"\n{'='*60}")
        print(f"Signal #{signal_count}")
        print(f"{'='*60}")
        print(f"Total pulses: {len(pulses)}")
        
        # 첫 20개 펄스 출력 (신호 패턴 확인)
        if len(pulses) > 0:
            print(f"Pulses (first 20): {list(pulses[:20])}")
        
        # 디코드 시도
        try:
            code = adafruit_irremote.decode_bits(pulses)
            print(f"Decoded: {code}")
            print(f"Code type: {type(code)}, Length: {len(code) if hasattr(code, '__len__') else 'N/A'}")
            
            if code:
                # NEC 코드는 4개 요소: (address, inverted_address, command, inverted_command)
                # 또는 2개 요소: (address, command)
                if isinstance(code, (list, tuple)):
                    if len(code) == 4:
                        # 확장 NEC 형식: (addr, ~addr, cmd, ~cmd)
                        addr, addr_inv, cmd, cmd_inv = code[0], code[1], code[2], code[3]
                        print(f"  ➤ Address: 0x{addr:02X} ({addr})")
                        print(f"  ➤ Command: 0x{cmd:02X} ({cmd})")
                        
                        # 맵에 저장
                        key = (addr, cmd)
                        if key not in signal_map:
                            signal_map[key] = {'count': 1, 'pulses': pulses}
                        else:
                            signal_map[key]['count'] += 1
                    elif len(code) >= 2:
                        addr, cmd = code[0], code[1]
                        print(f"  ➤ Address: 0x{addr:02X} ({addr})")
                        print(f"  ➤ Command: 0x{cmd:02X} ({cmd})")
                        
                        # 맵에 저장
                        key = (addr, cmd)
                        if key not in signal_map:
                            signal_map[key] = {'count': 1, 'pulses': pulses}
                        else:
                            signal_map[key]['count'] += 1
                    else:
                        print(f"  ➤ Code format unexpected: {code}")
                else:
                    print(f"  ➤ Code format unexpected: {code}")
        
        except adafruit_irremote.FailedToDecode as e:
            print(f"Failed to decode: {e}")
        except adafruit_irremote.IRDecodeException as e:
            print(f"IR decode error: {e}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
        
        print("\n다음 버튼을 누르세요...")

except KeyboardInterrupt:
    print("\n\n" + "=" * 60)
    print("수집 완료")
    print("=" * 60)
    
    print("\n고유 신호 목록:")
    print("-" * 60)
    
    if signal_map:
        # 신호를 Command 값으로 정렬
        sorted_signals = sorted(signal_map.items(), key=lambda x: x[0][1])
        
        for (addr, cmd), data in sorted_signals:
            print(f"\nAddress: 0x{addr:02X} | Command: 0x{cmd:02X}")
            print(f"  수신 횟수: {data['count']}")
            print(f"  펄스 개수: {len(data['pulses'])}")
        
        print("\n" + "=" * 60)
        print("버튼 매핑 정보:")
        print("=" * 60)
        print("\n다음 정보를 바탕으로 key_map을 업데이트하세요:")
        print("irremote_nonblocking.py의 decodeKeyValue() 함수 참고\n")
        
        print("Command 코드 목록:")
        for (addr, cmd), data in sorted_signals:
            print(f"  0x{cmd:02X}: \"버튼이름\",  # {data['count']}회 수신됨")
        
        print("\n" + "=" * 60)
        print("코드 형식 (4개 요소 NEC 프로토콜):")
        print("  (address, inverted_address, command, inverted_command)")
        print("  예: (0, 255, 0xA2, 0x5D)")
        print("=" * 60)
    else:
        print("\n수집된 신호가 없습니다!")
        print("버튼을 누르지 않았거나 신호를 받지 못했을 가능성이 있습니다.")
    
    print("\n" + "=" * 60)
    print("종료합니다.")
    
    try:
        receiver.deinit()
    except:
        pass
