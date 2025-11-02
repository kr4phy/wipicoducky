# IR 리모컨 신호 분석 및 맞춤 설정 가이드

## 문제: 모든 버튼이 같은 코드로 인식됨 (0xFF 등)

### 원인 분석

이 문제는 다음 중 하나일 가능성이 높습니다:

1. **NEC 프로토콜이 아님**: 리모컨이 다른 IR 프로토콜 사용 (RC5, RC6, SIRC 등)
2. **리모컨 신호 문제**: IR 수신기가 제대로 신호를 받지 못함
3. **디코더 설정 문제**: adafruit_irremote의 디코더가 이 리모컨에 맞지 않음

### 해결 방법

## 1단계: 신호 캡처 및 분석

### irremote_capture.py 실행

```bash
# Pico W REPL에서 실행
exec(open('irremote_capture.py').read())
```

이 스크립트는:
- 각 버튼의 원시 펄스 데이터를 수집
- 디코드된 address와 command 출력
- 사용 가능한 key_map 생성

### 기대되는 출력

```
============================================================
Signal #1
============================================================
Total pulses: 67
Pulses (first 20): [8973, 4484, 597, 551, ...]
Decoded: [0, 16]
  ➤ Address: 0x00 (0)
  ➤ Command: 0x10 (16)

다음 버튼을 누르세요...
```

## 2단계: 버튼별 신호 수집

다음 버튼들을 순서대로 누릅니다:

```
0, 1, 2, 3, 4, 5, 6, 7, 8, 9  (숫자 버튼)
+, -  (볼륨 조절)
CH+, CH-  (채널 조절)
PLAY/PAUSE, NEXT, PREV  (미디어 제어)
POWER  (전원)
```

## 3단계: 결과 분석

Ctrl+C로 종료하면 다음이 출력됩니다:

```
============================================================
수집 완료
============================================================

고유 신호 목록:
------------------------------------------------------------

Address: 0x00 | Command: 0x10
  수신 횟수: 1
  펄스 개수: 67

Address: 0x00 | Command: 0x11
  수신 횟수: 1
  펄스 개수: 67

...

============================================================
새로운 key_map (irremote_nonblocking.py에 추가):
============================================================

key_map = {
    0x10: "BUTTON_NAME",  # addr=0x00, cmd=0x10
    0x11: "BUTTON_NAME",  # addr=0x00, cmd=0x11
    ...
}
```

## 4단계: irremote_nonblocking.py 업데이트

캡처된 결과를 바탕으로 `decodeKeyValue()` 함수의 `key_map` 업데이트:

```python
def decodeKeyValue(data):
    """IR 원격 제어 키 코드를 문자열로 변환"""
    key_map = {
        0x10: "0",        # 실제 리모컨의 0번 버튼
        0x11: "1",        # 실제 리모컨의 1번 버튼
        0x12: "2",
        0x13: "3",
        0x14: "4",
        0x15: "5",
        0x16: "6",
        0x17: "7",
        0x18: "8",
        0x19: "9",
        0x1A: "+",        # 실제 리모컨의 + 버튼
        0x1B: "-",        # 실제 리모컨의 - 버튼
        # ... 나머지 버튼들
    }
    return key_map.get(data, f"UNKNOWN(0x{data:02X})")
```

## 모든 버튼이 0xFF로 나오는 경우

### 원인

- **NEC 프로토콜이 아님**: 리모컨이 다른 프로토콜 사용
- **신호 품질 문제**: IR 수신기가 신호를 제대로 수신하지 못함
- **주소 불일치**: NEC 프로토콜이지만 예상과 다른 주소 코드

### 진단

#### 1. 펄스 데이터 확인

irremote_capture.py에서 출력되는 펄스 데이터 확인:

```
Pulses (first 20): [8973, 4484, 597, 551, ...]
```

- **8973**: 너무 큼 (일반적으로 NEC 헤더는 9000 정도)
- **4484**: NEC 프로토콜 맞음
- **597, 551**: 논리 1과 0을 나타내는 펄스

NEC 프로토콜의 표준 펄스:
- Header: 9000 (ON) + 4500 (OFF)
- Bit 1: 560 (ON) + 1690 (OFF)
- Bit 0: 560 (ON) + 560 (OFF)

#### 2. 리모컨 유형 확인

펄스 패턴으로 프로토콜 식별:

```
NEC (표준):
  Header: 9000 + 4500
  Bits: 560
  
RC5 (Philips):
  Bits: 889
  
RC6 (Philips):
  Bits: 444
  
SIRC (Sony):
  Header: 2400 + 600
  Bits: 600
```

## 신호 품질 문제 해결

### 1. IR 수신기 위치 조정

```
┌─────────────────┐
│   Pico W        │
│  ┌───────────┐  │
│  │IR Receiver│  │  <- 리모컨을 이쪽으로 향하게
│  └───────────┘  │
└─────────────────┘
```

### 2. 리모컨 거리 조정

- 10-20cm 거리에서 테스트
- 너무 가까우면 신호 왜곡
- 너무 멀면 신호 약함

### 3. IR 수신기 민감도 확인

```python
# irremote_capture.py에서 max_pulse 값 조정
pulses = decoder.read_pulses(
    receiver, 
    blocking=True, 
    max_pulse=10000  # 기본값, 증가 가능
)
```

### 4. 리모컨 배터리 확인

배터리가 약하면 신호 강도 감소

## 고급 설정

### 수동 프로토콜 정의

만약 NEC 프로토콜이 아닌 경우, 커스텀 디코더 필요:

```python
# GenericTransmit/GenericDecode 사용으로 커스텀 가능
# https://docs.circuitpython.org/projects/irremote/en/latest/

from adafruit_irremote import GenericDecode

# 커스텀 헤더, 1, 0 파라미터 정의 필요
```

## 완전한 체크리스트

- [ ] irremote_capture.py 실행했는가?
- [ ] 모든 버튼의 신호가 다른 코드를 반환하는가?
- [ ] 펄스 데이터가 NEC 프로토콜과 일치하는가?
- [ ] key_map에 모든 버튼 추가했는가?
- [ ] irremote_nonblocking.py를 업데이트했는가?

## 문제 해결 요약

| 증상 | 원인 | 해결책 |
|------|------|--------|
| 모든 버튼 0xFF | NEC 프로토콜 아님 | capture로 신호 분석 |
| 펄스가 NEC와 다름 | 다른 IR 프로토콜 | 리모컨 모델 확인, 커스텀 디코더 |
| 신호가 약하거나 없음 | 수신기 위치/배터리 | 위치 조정, 배터리 교체 |

## 유용한 링크

- Adafruit IRRemote 문서:
  https://docs.circuitpython.org/projects/irremote/en/latest/

- IR 프로토콜 참고:
  https://en.wikipedia.org/wiki/Infrared_Data_Association

- NEC 프로토콜 상세:
  http://www.sbprojects.net/knowledge/ir/nec.php
