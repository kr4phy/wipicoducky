# GPIO 충돌 문제 해결 가이드

## 에러: `ValueError: GP17 in use`

이 에러는 GPIO 17(GP17)이 이미 다른 프로그램이나 모듈에서 사용 중일 때 발생합니다.

## 원인

### 1. **다른 프로그램이 GP17 사용 중**
- `code.py`나 `boot.py`에서 다른 목적으로 GP17 사용
- 이전 REPL 세션에서 초기화되지 않은 객체가 메모리에 남아있음

### 2. **CircuitPython 메모리 상태**
- REPL 세션이 완전히 종료되지 않음
- 가비지 컬렉션 미실행

### 3. **하드웨어 상태**
- Pico W가 완전히 리셋되지 않음

## 해결 방법 (우선순위순)

### 해결책 1: **Pico W 재시작 (가장 효과적)**

```bash
# 방법 1: 물리적 재시작
1. Pico W의 USB 케이블 뽑기
2. 5초 대기
3. 다시 연결

# 방법 2: REPL에서 소프트 리셋
Ctrl+D  # CircuitPython 소프트 리셋
```

### 해결책 2: **다른 GPIO 핀 사용**

현재 `code.py` 또는 `boot.py`를 확인하여 GP17이 사용되는지 체크:

```python
# 현재 사용 중인 핀 목록 확인
# 다음 핀들은 일반적으로 사용 가능:
# GP0, GP1, GP2, GP3, GP4, GP5, GP6, GP7, GP8, GP9, GP10, GP11, GP12, GP13, GP14, GP15, GP16, GP26, GP27, GP28

# GP17 대신 다른 핀 사용 (예: GP16)
```

### 해결책 3: **code.py / boot.py 비활성화**

Pico W를 MTP 모드로 마운트한 후:

```bash
# 1. code.py를 code.py.bak으로 이름 변경
# 2. Pico W 재시작
# 3. 이제 irremote_nonblocking.py 실행
```

## 현재 코드의 개선 사항

업데이트된 `irremote_nonblocking.py`에서는 다음을 추가했습니다:

```python
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
        print("1. Pico W를 재시작하세요...")
        raise
```

이제 자동으로 메모리 정리를 시도합니다.

## 조사 방법

### Pico W의 현재 프로그램 확인

**Pico W에 SSH/REPL 접속:**

```python
# REPL에서 실행
import microcontroller
import os

print("Current files:")
for f in os.listdir():
    print(f" - {f}")

print("\nRunning program: code.py or boot.py")
```

### 할당된 핀 확인

```python
# 현재 할당된 모든 핀 조회 (정확한 방법은 CircuitPython 버전에 따라 다름)
import board
print(dir(board))
```

## 핀 대안

GP17을 사용할 수 없는 경우 다음 핀 중 하나로 변경:

| 핀 | 상태 | 비고 |
|----|------|------|
| GP0-GP15 | 가능 | 일반 GPIO |
| **GP16** | **권장** | GP17과 유사하게 사용 가능 |
| GP26, GP27, GP28 | 가능 | ADC 핀으로도 사용 가능 |
| GP23 | ⚠️ LED | 보드 LED와 충돌 가능 |
| GP24 | ⚠️ VBUS | USB 전원 감지 |
| GP25 | ⚠️ LED | 보드 LED |

### 핀 변경 방법

```python
# irremote_nonblocking.py에서 다음 라인을 변경:
# receiver = pulseio.PulseIn(board.GP17, maxlen=200, idle_state=True)

# 예: GP16 사용
receiver = pulseio.PulseIn(board.GP16, maxlen=200, idle_state=True)

# 그리고 하드웨어 연결도 변경:
# IR Receiver의 OUT 핀 -> Pico W의 GP16 (대신 GP17)
```

## 하드웨어 확인

IR 수신기가 정말 GP17에 연결되었는지 다시 확인:

```
IR Receiver:
  VCC -> Pico W 3V3
  GND -> Pico W GND
  OUT -> Pico W GP17 ✓
```

## 완전 초기화 프로세스

문제가 계속되는 경우:

```bash
# 1. Pico W에서 모든 .py 파일 제거
#    - code.py, boot.py, 모든 프로그램

# 2. Pico W 재시작
#    - USB 뽑았다가 다시 꽂기

# 3. irremote_nonblocking.py 단독으로 실행
#    - REPL에서: exec(open('irremote_nonblocking.py').read())

# 4. 문제 없으면 다른 프로그램 추가
```

## 디버깅 스크립트

문제를 진단하기 위한 스크립트:

```python
# debug_gpio.py
import board
import time

print("=" * 50)
print("GPIO 진단 스크립트")
print("=" * 50)

# 현재 실행 중인 코드 확인
import os
print("\n현재 Pico W의 파일:")
for f in os.listdir():
    print(f"  - {f}")

# GP17 상태 확인
try:
    import pulseio
    print("\nGP17 테스트 중...")
    test_pin = pulseio.PulseIn(board.GP17, maxlen=10, idle_state=True)
    print("✓ GP17 사용 가능")
    test_pin.deinit()
except ValueError as e:
    print(f"✗ GP17 충돌: {e}")
except Exception as e:
    print(f"✗ 오류: {e}")

# 다른 핀 테스트
pins_to_test = [board.GP16, board.GP15, board.GP14, board.GP13]
print("\n다른 핀 테스트:")
for pin in pins_to_test:
    try:
        test = pulseio.PulseIn(pin, maxlen=10, idle_state=True)
        print(f"✓ {pin} 사용 가능")
        test.deinit()
    except ValueError:
        print(f"✗ {pin} 충돌")
    except Exception as e:
        print(f"? {pin} 오류: {e}")

print("\n진단 완료")
```

## 참고 사항

- **CircuitPython은 단 하나의 프로세스만 실행**: 
  - `code.py`를 실행 중이면 REPL에서 다른 프로그램 실행 불가
  - `code.py` 종료 후 REPL 접속 필요

- **핀 권한은 반환되어야 함**:
  - 프로그램이 종료되면 자동으로 반환됨
  - REPL 세션 종료 = Pico W 재시작 필요

## 최종 체크리스트

- [ ] Pico W 재시작했는가?
- [ ] 다른 프로그램(code.py, boot.py)이 GP17 사용하는가?
- [ ] IR 수신기가 GP17에 올바르게 연결되었는가?
- [ ] USB 케이블이 제대로 연결되었는가?
- [ ] CircuitPython이 최신 버전인가?

문제가 해결되지 않으면 위 체크리스트를 따라 진행하세요!
