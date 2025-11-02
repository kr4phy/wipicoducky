# IR 리모컨 설정 가이드

## 업데이트: API Reference 기반 구현

이제 공식 API Reference에 따라 올바르게 구현되었습니다.

## 코드 버전

두 가지 버전을 제공합니다:

### 1. **irremote.py** (기본 버전)
- `GenericDecode` + `read_pulses()` 사용
- 블로킹 모드
- 간단하고 직관적

### 2. **irremote_nonblocking.py** (권장 버전)
- `NonblockingGenericDecode` 사용
- 비블로킹 모드
- 더 견고하고 반응성 좋음
- 권장: `irremote_nonblocking.py` 사용

## 문제: `AttributeError: 'module' object has no attribute 'NEC'`

이 에러는 `adafruit_irremote` 라이브러리가 올바르게 설치되지 않았을 때 발생합니다.

## 해결 방법

### 1. 라이브러리 파일 확인

필요한 파일들이 `lib/` 폴더에 있는지 확인하세요:

```
lib/
  adafruit_irremote/
    __init__.mpy
```

### 2. 라이브러리 설치

#### 옵션 A: CircuitPython Bundle (권장)

1. https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases 에서 최신 Bundle 다운로드
2. `adafruit-circuitpython-irremote` 폴더를 찾으세요
3. 안의 `adafruit_irremote` 폴더를 Pico W의 `lib/` 폴더에 복사

#### 옵션 B: 수동 설치

https://github.com/adafruit/Adafruit_CircuitPython_IRRemote 에서 최신 버전을 다운로드:

```bash
# Windows (PowerShell)
# 1. 라이브러리 다운로드
# 2. adafruit_irremote 폴더를 lib/ 에 복사
xcopy adafruit_irremote C:\path\to\pico\lib\adafruit_irremote /E /I
```

### 3. CircuitPython 버전 확인

Pico W의 CircuitPython 버전을 확인하세요:

```bash
# boot_out.txt에서 확인
# 예: Adafruit CircuitPython 10.0.3
```

호환되는 라이브러리를 다운로드하세요:
- CircuitPython 9.x → Bundle 9.x
- CircuitPython 10.x → Bundle 10.x

### 4. 정상 작동 확인

CircuitPython REPL에서 테스트:

```python
>>> import adafruit_irremote
>>> adafruit_irremote.GenericDecode()
<adafruit_irremote.GenericDecode object at 0x...>  # 성공!
```

정상이면 위와 같이 객체가 생성됩니다.

## API 설명

### GenericDecode (블로킹 모드)

```python
decoder = adafruit_irremote.GenericDecode()
pulses = decoder.read_pulses(receiver, blocking=True)
code = adafruit_irremote.decode_bits(pulses)
```

**장점:**
- 간단한 구조
- 직관적인 코드

**단점:**
- 블로킹: UI가 반응하지 않을 수 있음

### NonblockingGenericDecode (비블로킹 모드) - 권장

```python
decoder = adafruit_irremote.NonblockingGenericDecode(receiver)
for message in decoder.read():
    if isinstance(message, adafruit_irremote.IRMessage):
        code = message.code
    elif isinstance(message, adafruit_irremote.NECRepeatIRMessage):
        # 반복 신호
        pass
```

**장점:**
- 비블로킹: 시스템이 반응성 유지
- 메시지 타입 분류 (IRMessage, NECRepeatIRMessage, UnparseableIRMessage)
- 더 견고한 에러 처리

**단점:**
- 코드가 약간 더 복잡함

## 메시지 타입

### IRMessage
정상적으로 디코된 IR 메시지
```python
message.code  # (address, command) 형식
```

### NECRepeatIRMessage
NEC 프로토콜의 반복 신호 (같은 버튼을 계속 누를 때)
```python
message.pulses  # 펄스 데이터
```

### UnparseableIRMessage
파싱하지 못한 IR 메시지
```python
message.pulses  # 펄스 데이터
# 무시하거나 로깅할 수 있음
```

## 예외 처리

| 예외 | 설명 | 처리 |
|------|------|------|
| `IRDecodeException` | 일반 디코드 예외 | 무시 또는 로깅 |
| `IRNECRepeatException` | NEC 반복 신호 | 무시 가능 |
| `FailedToDecode` | 디코드 실패 | 무시 또는 로깅 |

## 핫웨어 확인

### IR 수신기 연결

| IR Receiver | Pico W |
|-----------|---------|
| VCC       | 3V3     |
| GND       | GND     |
| OUT (Signal) | GP17  |

### 테스트 코드

```python
import board
import pulseio
import time
import adafruit_irremote

# 신호 수신 테스트
receiver = pulseio.PulseIn(board.GP17, maxlen=200, idle_state=True)
decoder = adafruit_irremote.GenericDecode()

print("리모컨 버튼을 누르세요...")
for i in range(5):
    pulses = decoder.read_pulses(receiver, blocking=True)
    print(f"수신: {len(pulses)} pulses")
    try:
        code = adafruit_irremote.decode_bits(pulses)
        print(f"코드: {code}")
    except Exception as e:
        print(f"디코드 실패: {e}")
```

## 문제 해결

### ImportError: no module named 'adafruit_irremote'

```
해결: lib/ 폴더에 adafruit_irremote 라이브러리 복사
```

### AttributeError: 'module' object has no attribute 'NEC'

```
원인: 최신 API에서는 NEC() 클래스가 없음
해결: GenericDecode() 또는 NonblockingGenericDecode() 사용
```

### 신호를 받지만 디코드 오류 발생

```
원인: IR 신호 품질 저하
해결:
1. IR 수신기 위치 조정
2. 리모컨 배터리 확인
3. pulseio maxlen 값 증가 (최대 512)
4. decoder 매개변수 조정
```

### 신호를 받지 못함

```
확인 사항:
1. IR 수신기 전원 확인 (3V3 연결)
2. 신호 핀 확인 (GP17 연결)
3. 리모컨 작동 확인 (다른 장치에서 테스트)
```

## 권장 사용

**새 프로젝트는 `irremote_nonblocking.py` 사용을 권장합니다:**

```bash
# 기본 버전에서 비블로킹으로 변경
cp irremote_nonblocking.py irremote.py
```

이유:
- 더 견고한 에러 처리
- 비블로킹 모드로 시스템 반응성 향상
- 공식 API 권장 방식

## 참고 자료

- Adafruit CircuitPython IRRemote 문서:
  https://docs.circuitpython.org/projects/irremote/en/latest/

- CircuitPython Bundle:
  https://github.com/adafruit/Adafruit_CircuitPython_Bundle

- IR Protocol (NEC):
  https://en.wikipedia.org/wiki/Infrared_Data_Association

## 성공 사례

정상 작동 시 다음과 같이 출력됩니다:

```
IR -> HID ready (NonblockingGenericDecode mode)
addr: 0x00 cmd: 0x16 => 0
addr: 0x00 cmd: 0x0C => 1
addr: 0x00 cmd: 0x18 => 2
NEC repeat signal
...
```

## 버전 히스토리

### v2 (현재) - API Reference 기반
- GenericDecode + decode_bits() 사용
- NonblockingGenericDecode 추가
- 공식 API에 완벽하게 준수

### v1 (이전)
- NEC() 클래스 사용 (더 이상 지원되지 않음)
- 에러 처리 미흡

