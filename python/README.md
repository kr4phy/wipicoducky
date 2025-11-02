# Advanced Ducky Script C2 Server

## Overview

This is an advanced Command & Control (C2) server for managing Rubber Ducky HID injection attacks with AI-powered automation capabilities.

## Features

### 1. Manual Script Execution
- Execute custom Ducky scripts manually
- Upload and run script files
- Real-time execution feedback

### 2. Script Templates
Pre-configured attack templates:
- `download_backdoor.dd` - Download and execute backdoor payload
- `reverse_shell.dd` - Establish reverse shell connection
- `open_calculator.dd` - Simple test script
- `exfiltrate_passwords.dd` - Extract browser passwords
- `disable_defender.dd` - Disable Windows Defender

### 3. Payload Server
Serve backdoor payloads to target machines:
- `backdoor.ps1` - PowerShell backdoor with auto-reconnect
- `reverse_shell.py` - Python reverse shell

### 4. AI-Powered HID Injection
Use LLM to automatically generate and execute HID injection attacks:
- Natural language attack objectives
- Automated script generation
- Support for multiple providers:
  - **Ollama** (Local): phi4:mini, llama2, mistral, etc. - Completely private, no cloud dependency
  - **OpenRouter** (Cloud): devstral-small-2505 (free), and many other models
- Real-time execution and feedback

### 5. Reverse Shell Management
Built-in reverse shell listener:
- Multiple concurrent sessions
- Interactive command execution
- Session management

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Option 1: Install Ollama (for local AI features)
# Windows: Download from https://ollama.ai/download
# Linux: curl -fsSL https://ollama.ai/install.sh | sh
# Mac: brew install ollama

# Pull the default model
ollama pull phi4:mini

# Option 2: Use OpenRouter (for cloud AI features)
# Sign up at https://openrouter.ai
# Get free API key at https://openrouter.ai/keys
# Free model: devstral-small-2505 (recommended for Ducky scripts)
```

## Usage

### Basic Server

```bash
python c2server.py
```

Access the web interface at `http://localhost:5000`

### Custom Configuration

```bash
python c2server.py --host 0.0.0.0 --port 8080 --shell-port 4444
```

### Configuring Templates

Edit templates in `python/templates/` directory. Replace `ATTACKER_IP` with your actual IP address:

```bash
# Linux/Mac
sed -i 's/ATTACKER_IP/192.168.1.100/g' templates/*.dd

# Windows PowerShell
(Get-Content templates\*.dd) -replace 'ATTACKER_IP','192.168.1.100' | Set-Content templates\*.dd
```

## Web Interface

### Manual Tab
Execute custom Ducky scripts by typing or uploading files.

### Templates Tab
Browse and execute pre-configured attack templates with one click.

### AI Assistant Tab
1. Enable AI Assistant
2. Select Provider:
   - **Ollama (Local)**: For privacy and offline use
     - Enter model name (e.g., `phi4:mini`, `llama2`, `mistral`)
     - Configure Ollama URL (default: `http://localhost:11434`)
   - **OpenRouter (Cloud)**: For more powerful models
     - Enter model name (e.g., `devstral-small-2505`)
     - Enter your OpenRouter API key (get free at https://openrouter.ai/keys)
3. Click "Initialize Model"
4. Enter attack objective in natural language
5. Click "Generate & Execute Attack"

Example objectives:
- "Open calculator and type hello"
- "Open notepad and write a message"
- "Download file from web server"

### Payloads Tab
View and download available payload files. Payloads are served at:
```
http://YOUR_IP:5000/payloads/filename
```

### Reverse Shells Tab
- View active reverse shell sessions
- Execute commands on compromised machines
- Real-time command output

## Security Warning

⚠️ **FOR EDUCATIONAL PURPOSES ONLY**

This tool is designed for:
- Security research
- Penetration testing (with authorization)
- Red team exercises
- Educational demonstrations

**DO NOT** use this tool for:
- Unauthorized access to systems
- Malicious purposes
- Illegal activities

Always obtain proper authorization before testing on any system you don't own.

## Architecture

```
c2server.py          # Main Flask server
├── templates/       # Ducky script templates
│   ├── download_backdoor.dd
│   ├── reverse_shell.dd
│   └── ...
├── payloads/        # Backdoor payloads
│   ├── backdoor.ps1
│   └── reverse_shell.py
└── requirements.txt # Python dependencies
```

## API Endpoints

- `GET /` - Web interface
- `POST /execute` - Execute Ducky script
- `GET /api/templates` - List templates
- `GET /api/template/<name>` - Get template content
- `GET /api/payloads` - List payloads
- `GET /payloads/<filename>` - Download payload
- `POST /api/llm/init` - Initialize LLM model
- `POST /api/llm/attack` - Generate AI attack
- `GET /api/shells` - List reverse shells
- `POST /api/shell/command` - Execute shell command

## LLM Models

Ollama models you can use:

- **Default**: `phi4:mini` (recommended, ~2GB, fast and capable)
- **Lightweight**: `phi3:mini` (~2GB)
- **Balanced**: `llama2` (~4GB)
- **Advanced**: `mistral` (~4GB)
- **Large**: `llama2:13b` (~7GB, slower but more accurate)

Pull models with: `ollama pull <model-name>`

See all available models: https://ollama.ai/library

## Troubleshooting

### LLM Not Working

**For Ollama:**
- Ensure Ollama is installed and running
- Check Ollama service: `ollama serve`
- Verify model is pulled: `ollama list`
- Test connection: `curl http://localhost:11434/api/tags`

**For OpenRouter:**
- Verify API key is correct (starts with `sk-or-v1-`)
- Check internet connection
- Ensure you have credits (free tier available)
- Test at: https://openrouter.ai/playground

### Reverse Shell Not Connecting
- Check firewall settings
- Verify correct IP address in templates
- Ensure port 4444 (or custom port) is open

### Pico W Not Responding
- Verify Pico W is connected and running CircuitPython
- Check IP address (default: 192.168.4.1)
- Test connection manually

## Contributing

This is an educational project. Improvements welcome:
- Additional templates
- Better LLM prompts
- UI enhancements
- Bug fixes

## License

Educational use only. Use responsibly and legally.
