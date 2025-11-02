# Quick Start Guide

## 1. Basic Setup

```powershell
# Navigate to project directory
cd c:\Users\kr4ph\Development\pico

# Activate virtual environment
.\.venv\Scripts\activate

# Install required dependencies
pip install flask requests

# Option 1: Install Ollama for local AI features (recommended)
# Download from https://ollama.ai/download
# Then pull a model:
ollama pull phi4:mini

# Option 2: Use OpenRouter for cloud AI features
# Sign up at https://openrouter.ai
# Get free API key at https://openrouter.ai/keys
# Free model available: devstral-small-2505
```

## 2. Configure Templates

Before using, update the `ATTACKER_IP` in templates with your actual IP:

```powershell
# Find your IP address
ipconfig

# Update templates (replace 192.168.1.100 with your IP)
$files = Get-ChildItem python\templates\*.dd
foreach ($file in $files) {
    (Get-Content $file.FullName) -replace 'ATTACKER_IP','192.168.1.100' | Set-Content $file.FullName
}

# Update payloads
$files = Get-ChildItem python\payloads\*.ps1
foreach ($file in $files) {
    (Get-Content $file.FullName) -replace 'ATTACKER_IP','192.168.1.100' | Set-Content $file.FullName
}
```

## 3. Start the Server

```powershell
# Start C2 server (default: http://0.0.0.0:5000)
python python\c2server.py

# Or with custom settings
python python\c2server.py --host 0.0.0.0 --port 8080 --shell-port 4444
```

## 4. Access Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

## 5. Using the Interface

### Manual Tab
- Type or paste Ducky script
- Or click "Choose File" to upload a .dd file
- Click "Execute Script" to run on target

### Templates Tab
- Browse pre-configured attack scripts
- Click "View" to see script content
- Click "Execute" to run directly

### AI Assistant Tab
1. Check "Enable AI Assistant"
2. Select Provider:
   - **Ollama (Local)**: 
     - Enter model name (default: `phi4:mini`)
     - Verify Ollama URL (default: `http://localhost:11434`)
   - **OpenRouter (Cloud)**:
     - Enter model name (default: `devstral-small-2505` - free)
     - Enter your API key from https://openrouter.ai/keys
3. Click "Initialize Model"
4. Type attack objective in plain English
5. Click "Generate & Execute Attack"

Example objectives:
- "Open notepad and type hello world"
- "Open calculator"
- "Open command prompt and show directory listing"

### Payloads Tab
- View available backdoor files
- Click "Download" to get the payload URL
- Use in Ducky scripts with download_backdoor template

### Reverse Shells Tab
- Shows active connections from compromised machines
- Type commands and press "Send" to execute
- Output appears in the terminal below

## 6. Testing with Pico W

Make sure your Raspberry Pi Pico W is:
1. Running CircuitPython with the updated `webapp.py`
2. Connected to your network
3. Reachable at 192.168.4.1 (or update PICO_URL in c2server.py)

Test with the calculator template:
```
Templates Tab → open_calculator.dd → Execute
```

## 7. Troubleshooting

### "Connection refused" errors
- Check Pico W is powered and running
- Verify IP address (try pinging 192.168.4.1)
- Ensure CircuitPython code is loaded

### AI features not working
```powershell
# Install Ollama from https://ollama.ai/download

# Start Ollama service
ollama serve

# Pull the model
ollama pull phi4:mini

# Test Ollama
ollama run phi4:mini "Hello"
```

### Reverse shell not connecting
- Check firewall allows incoming connections on port 4444
- Update ATTACKER_IP in templates with correct IP
- Test with: `Test-NetConnection -ComputerName localhost -Port 4444`

## 8. Example Attack Flow

### Simple Test
1. Go to Templates tab
2. Click Execute on `open_calculator.dd`
3. Target machine should open calculator

### Reverse Shell
1. Update `reverse_shell.dd` with your IP
2. Go to Templates tab
3. Execute `reverse_shell.dd`
4. Switch to "Reverse Shells" tab
5. Wait for connection (should appear in seconds)
6. Type commands like `whoami`, `dir`, etc.

### AI-Powered Attack
1. Install and start Ollama
2. Go to AI Assistant tab
3. Enable and initialize with `phi4:mini`
4. Enter: "Open notepad and type hello"
5. Click Generate & Execute
6. Watch the AI create and run the script

## 9. Safety Reminders

⚠️ **IMPORTANT:**
- Only use on systems you own or have permission to test
- This is for educational and authorized testing ONLY
- Disable antivirus on target for testing (with permission)
- Keep attack scripts generic for demos

## 10. Advanced Usage

### Custom Model for AI
```powershell
# Available Ollama models:
ollama pull phi4:mini      # Default, recommended
ollama pull phi3:mini      # Lightweight
ollama pull llama2         # Larger, more capable
ollama pull mistral        # Advanced reasoning

# List installed models
ollama list
```

### Creating Custom Templates
1. Create new .dd file in `python/templates/`
2. Use standard Ducky Script syntax
3. Refresh Templates tab to see it

### Adding Custom Payloads
1. Place executable/script in `python/payloads/`
2. Reference in templates via `/payloads/filename`
3. Example: `http://YOUR_IP:5000/payloads/mybadge.exe`

## 11. Command Reference

Common Ducky Script commands:
```
GUI r           # Open Run dialog (Win+R)
STRING text     # Type text
ENTER           # Press Enter
DELAY 1000      # Wait 1 second (milliseconds)
CTRL x          # Control+X
ALT F4          # Alt+F4
SHIFT           # Hold Shift
```

## 12. Next Steps

- Read full `README.md` for detailed documentation
- Explore more advanced templates
- Customize AI prompts for better results
- Integrate with other security tools

Happy testing! 🦆
