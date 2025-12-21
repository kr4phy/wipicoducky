# wipicoducky

이 프로젝트는 https://github.com/dbisu/pico-ducky 를 기반으로 만들어진 프로젝트입니다.
원본 프로젝트는 Dave Bailey (@dbisu)가 작성하였고, 본 프로젝트는 해당 프로젝트의 일부를 사용합니다.

라이선스
- 본 저장소 및 파생작은 GNU General Public License version 2 (GPLv2) 하에 배포됩니다. 자세한 라이선스 전문은 `LICENSE` 파일을 확인하세요.

크레딧
- 원작자: Dave Bailey (dbisu) — https://github.com/dbisu/pico-ducky
- 변경: kr4phy (현재 저장소)

개요
- Pico (CircuitPython) 기반으로 IR 리모컨 또는 Web UI를 통해 Ducky 스크립트(USB HID 입력)를 실행하도록 구현한 코드 모음입니다.
- 주요 파일:
  - `circuitpython/irremote_nonblocking.py` — NonblockingGenericDecode 사용, IR -> HID, 리모컨 버튼으로 ducky 스크립트 실행
  - `circuitpython/irremote.py` — (blocking 버전)
  - `circuitpython/irremote_capture.py` — IR 신호 캡처/분석 도구
  - `circuitpython/ducky.py` — Ducky 스크립트 파서 및 실행기 (원본 코드 기반)

주의사항 (Safety / Usage)
- 이 코드들은 USB HID (키보드/컨슈머) 장치를 통해 키 입력을 자동으로 전송합니다. 잘못 사용하면 의도치 않은 명령이 실행되어 시스템에 영향을 줄 수 있습니다.
- 로컬 테스트 시 Pico의 `circuitpy` 드라이브에 파일을 복사하고, 대상 키보드 입력을 받을 준비가 된 테스트 시스템(예: 안전한 가상머신)에서 확인하세요.
- 상업적 또는 악의적 목적으로의 사용을 금지합니다. GPLv2 규정에 따라 소스 공개가 요구됩니다.

간단한 사용법
1. Pico W에 CircuitPython이 설치되어 있는지 확인합니다.
2. `lib/` 폴더에 필요한 CircuitPython 라이브러리(`adafruit_irremote`, `adafruit_hid` 등)를 넣습니다.
3. `circuitpython/` 폴더의 파일들을 Pico의 루트 (CIRCUITPY) 폴더로 복사합니다.
4. Pico를 연결한 상태에서 REPL로 접속하거나, 자동 실행을 통해 `irremote_nonblocking.py`가 동작하도록 합니다.
5. 리모컨으로 숫자(0-9)를 눌러 각 인덱스의 Ducky 스크립트를 실행할 수 있습니다. (스크립트는 `irremote_nonblocking.py`의 `irremote_payloads` 리스트에 정의되어 있습니다.)

법적 고지
- 본 저장소는 원저작자의 동의 하에 포크/수정되었음을 밝힙니다. 원저작자와 본 저장소의 저작권 표시는 `LICENSE` 파일을 확인하세요.

문의
- 프로젝트 소유자: kr4phy (저장소 소유자)

---
*이 파일은 원본 `pico-ducky` 프로젝트(GPLv2)를 기반으로 작성되었습니다.*
