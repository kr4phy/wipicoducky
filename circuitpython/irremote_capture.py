# 간단한 IR 신호 분석 (디버깅용)
import board
import pulseio
import time
import adafruit_irremote

print("=" * 60)
print("Simple IR Debug - 신호 수집 및 분석")
print("=" * 60)
print("\n리모컨 버튼을 누르세요 (Ctrl+C로 종료)\n")

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

try:
    while True:
        # 펄스 수집
        pulses = decoder.read_pulses(receiver, blocking=True, max_pulse=10000)
        
        if pulses is None:
            continue
        
        signal_count += 1
        print(f"\n{'='*60}")
        print(f"Signal #{signal_count}")
        print(f"{'='*60}")
        print(f"Total pulses: {len(pulses)}")
        
        # 첫 30개 펄스 출력
        if len(pulses) > 0:
            print(f"Pulses (first 30): {list(pulses[:30])}")
        
        # 여러 디코더로 시도
        try:
            code = adafruit_irremote.decode_bits(pulses)
            print(f"\n[decode_bits] Code: {code}")
            print(f"Type: {type(code)}, Length: {len(code) if hasattr(code, '__len__') else 'N/A'}")
            
            if isinstance(code, (list, tuple)):
                for i, val in enumerate(code):
                    print(f"  code[{i}] = 0x{val:02X} ({val})")
        
        except Exception as e:
            print(f"decode_bits error: {type(e).__name__}: {e}")
        
        print("\n다음 버튼을 누르세요...")

except KeyboardInterrupt:
    print("\n\n종료합니다.")
    try:
        receiver.deinit()
    except:
        pass
