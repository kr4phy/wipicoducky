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
- 주요 기능:
  - IR 리모컨 신호 수신 및 Ducky 스크립트 매핑
  - Web UI를 통한 스크립트 선택 및 실행 (Pico W 전용)
  - Ducky 스크립트 파싱 및 실행
  - AI 활용 자연어 명령을 통한 HID 입력 생성

주의사항 (Safety / Usage)
- 이 코드들은 USB HID (키보드/컨슈머) 장치를 통해 키 입력을 자동으로 전송합니다. 잘못 사용하면 의도치 않은 명령이 실행되어 시스템에 영향을 줄 수 있습니다.
- 로컬 테스트 시 Pico의 `circuitpy` 드라이브에 파일을 복사하고, 대상 키보드 입력을 받을 준비가 된 테스트 시스템(예: 안전한 가상머신)에서 확인하세요.
- AI 기능 사용 시, 생성된 HID 입력이 예상과 다를 수 있으므로 주의가 필요합니다.
- GPLv2 규정에 따라 소스 공개가 요구됩니다.

사용법
1. Pico W에 CircuitPython이 설치되어 있는지 확인합니다.
3. `circuitpython/` 폴더의 파일들을 Pico의 루트 (CIRCUITPY) 폴더로 복사합니다.
4. `irremote.py 또는 wipicoducky.py`의 코드를 code.py 파일에 저장합니다.
5. `irremote.py` 사용시 리모컨으로 숫자(0-9)를 눌러 각 인덱스의 Ducky 스크립트를 실행할 수 있습니다. (스크립트는 `irremote.py`의 `irremote_payloads` 리스트에 정의되어 있습니다.)
6. `wipicoducky.py` 사용시 Web UI에 접속하여 스크립트를 선택하고 실행할 수 있습니다. (Pico W 전용) Web UI를 사용하려면 python/c2server.py를 실행하여 스크립트 서버를 시작해야 합니다. AI 기능을 사용하려면 ollama 서버를 별도로 실행해야 합니다.

Web UI 사용시 주의사항
- `secrets.py`에서 정의한 AP에 접속한 후 사용해야 합니다.
- LLM 사용시 예상치 못한 결과가 발생할 수 있으며 이에 대한 책임은 사용자에게 있습니다.

문의
- 프로젝트 소유자: kr4phy (저장소 소유자)
