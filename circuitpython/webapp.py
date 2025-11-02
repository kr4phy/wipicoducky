import socketpool
import time
import os
import json
import storage
import asyncio
import wsgiserver as server
from adafruit_wsgi.wsgi_app import WSGIApp
import wifi
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
import ducky


index_html = """<!doctype html>
<html>
    <head>
        <title>Pico W</title>
    </head>
    <body>
        <h1>It works!</h1>
    </body>
</html>"""

web_app = WSGIApp()
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)
kc = {
    "F1": Keycode.F1,
    "F2": Keycode.F2,
    "F3": Keycode.F3,
    "F4": Keycode.F4,
    "F5": Keycode.F5,
    "F6": Keycode.F6,
    "F7": Keycode.F7,
    "F8": Keycode.F8,
    "F9": Keycode.F9,
    "F10": Keycode.F10,
    "F11": Keycode.F11,
    "F12": Keycode.F12,
    "GUI": Keycode.GUI,
    "LCTRL": Keycode.LEFT_CONTROL,
    "RCTRL": Keycode.RIGHT_CONTROL,
    "LALT": Keycode.LEFT_ALT,
    "RALT": Keycode.RIGHT_ALT,
    "LSHIFT": Keycode.LEFT_SHIFT,
    "RSHIFT": Keycode.RIGHT_SHIFT,
    "TAB": Keycode.TAB,
    "ENTER": Keycode.ENTER,
    "BSPACE": Keycode.BACKSPACE,
    "ESC": Keycode.ESCAPE,
    "UARR": Keycode.UP_ARROW,
    "DARR": Keycode.DOWN_ARROW,
    "LARR": Keycode.LEFT_ARROW,
    "RARR": Keycode.RIGHT_ARROW,
    "INS": Keycode.INSERT,
    "DEL": Keycode.DELETE,
    "HOME": Keycode.HOME,
    "END": Keycode.END,
    "PGUP": Keycode.PAGE_UP,
    "PGDOWN": Keycode.PAGE_DOWN,
    "PRTSC": Keycode.PRINT_SCREEN,
}

def url_decode(s):
    s = s.replace('+', ' ')
    i = 0
    result = []
    while i < len(s):
        if s[i] == '%' and i + 2 < len(s):
            try:
                result.append(chr(int(s[i+1:i+3], 16)))
                i += 3
            except:
                result.append(s[i])
                i += 1
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)

def parse_post_data(request):
    # Try to determine content type for better parsing / logging
    content_type = None
    try:
        # WSGI request implementations may expose headers or environ
        content_type = getattr(request, 'headers', {}).get('Content-Type')
    except Exception:
        content_type = None
    try:
        if not content_type:
            content_type = request.environ.get('CONTENT_TYPE')
    except Exception:
        pass

    raw = request.body.getvalue()
    # log content-type and body length for debugging
    try:
        print(f"parse_post_data: Content-Type={content_type} body_len={len(raw) if raw is not None else 0}")
    except Exception:
        pass
    # request.body.getvalue() may return bytes on some versions; normalize to str
    if isinstance(raw, bytes):
        try:
            data = raw.decode('utf-8')
        except:
            data = raw.decode('latin-1')
    else:
        data = str(raw)

    data = data.strip()
    if not data:
        return {}

    # If Content-Type is JSON, parse JSON and return dict
    if content_type and 'application/json' in content_type.lower():
        try:
            # decode raw to text then parse json
            if isinstance(raw, bytes):
                raw_text = raw.decode('utf-8', errors='ignore').strip()
            else:
                raw_text = str(raw).strip()
            j = json.loads(raw_text)
            if isinstance(j, dict):
                # convert values to strings for compatibility
                return {k: (v if isinstance(v, str) else str(v)) for k, v in j.items()}
        except Exception as e:
            print('parse_post_data: JSON parse error:', e)
            # fall through to form parsing

    fields = data.split("&")
    parsed_data = {}
    for field in fields:
        if not field:
            # skip empty field produced by trailing & or empty body parts
            continue
        if '=' in field:
            key, value = field.split('=', 1)
            key = url_decode(key)
            parsed_data[key] = url_decode(value)
        else:
            # no '=' present, treat as flag with empty value
            parsed_data[url_decode(field)] = ''
    return parsed_data

# Simple execution lock/cooldown to prevent overlapping or rapid re-runs
execution_in_progress = False
last_exec_time = 0
COOLDOWN_SECONDS = 0.25

@web_app.route("/")
def index(request):
    response = index_html
    print(request.body)
    print(request.body.getvalue())
    return("200 OK", [('Content-Type', 'text/html')], response)

@web_app.route("/api/executeCommand/", methods=["POST"])
def api_run(request):
    global execution_in_progress, last_exec_time
    try:
        data = parse_post_data(request)
        cmd = data.get("cmd", "")

        # Fallback: if form parsing didn't yield 'cmd', try to parse JSON body
        if not cmd:
            try:
                raw = request.body.getvalue()
                if isinstance(raw, bytes):
                    raw_text = raw.decode('utf-8', errors='ignore').strip()
                else:
                    raw_text = str(raw).strip()

                if raw_text:
                    try:
                        j = json.loads(raw_text)
                        # accept a few common key names
                        cmd = j.get('cmd') or j.get('script') or j.get('command') or j.get('data') or ''
                        if cmd:
                            print("api_run: extracted 'cmd' from JSON body")
                    except Exception:
                        # not JSON or failed to parse — ignore and fall through
                        pass
            except Exception as e:
                print("api_run: error reading raw body for JSON fallback:", e)

        if not cmd:
            print("api_run: no 'cmd' in POST data")
            return ("400 Bad Request", [('Content-Type', 'application/json')], '{"status":"error","error":"no cmd provided"}')

        now = time.monotonic()
        # enforce cooldown
        if (now - last_exec_time) < COOLDOWN_SECONDS or execution_in_progress:
            print("api_run: rejected due to cooldown or busy")
            return ("429 Too Many Requests", [('Content-Type', 'application/json')], '{"status":"error","error":"cooldown or busy"}')

        execution_in_progress = True
        try:
            ducky.runScript(cmd)
        except Exception as e:
            print("Error running ducky script:", e)
            return ("500 Internal Server Error", [('Content-Type', 'application/json')], ('{"status":"error","error":"' + str(e) + '"}'))
        finally:
            execution_in_progress = False
            last_exec_time = time.monotonic()

        return ("200 OK", [('Content-Type', 'application/json')], '{"status":"success"}')
    except Exception as e:
        # any unexpected parsing/runtime error should still return a proper HTTP response
        print("api_run: unexpected error:", e)
        return ("500 Internal Server Error", [('Content-Type', 'application/json')], ('{"status":"error","error":"' + str(e) + '"}'))

async def start_web_service():
    
    HOST = repr(wifi.radio.ipv4_address_ap)
    PORT = 80        # Port to listen on
    print(HOST,PORT)

    wsgiServer = server.WSGIServer(PORT, application=web_app)

    print(f"open this IP in your browser: http://{HOST}:{PORT}/")

    # Start the server
    wsgiServer.start()
    while True:
        wsgiServer.update_poll()
        await asyncio.sleep(0)
