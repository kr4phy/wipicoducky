# Ollama Setup Guide

## What is Ollama?

Ollama is a local LLM (Large Language Model) runtime that allows you to run AI models on your own machine without cloud dependencies. It's faster, more private, and doesn't require internet after initial setup.

## Installation

### Windows

1. Download Ollama installer:
   - Visit: https://ollama.ai/download
   - Download the Windows installer
   - Run the installer and follow prompts

2. Verify installation:
   ```powershell
   ollama --version
   ```

### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### macOS

```bash
brew install ollama
```

## Getting Started

### 1. Start Ollama Service

```powershell
# Ollama runs as a service on Windows automatically
# Check if it's running:
curl http://localhost:11434/api/tags
```

If not running, start it manually:
```powershell
ollama serve
```

### 2. Pull a Model

Download the default model (phi4:mini):
```powershell
ollama pull phi4:mini
```

This will download ~2GB. First pull takes a few minutes.

### 3. Test the Model

```powershell
ollama run phi4:mini "Write a hello world program"
```

### 4. List Available Models

```powershell
# See what you have installed
ollama list

# Browse all available models
# Visit: https://ollama.ai/library
```

## Recommended Models for C2 Server

### phi4:mini (Default)
- **Size**: ~2GB
- **Speed**: Fast
- **Quality**: Excellent for scripting tasks
- **Recommended**: ✅ Yes

```powershell
ollama pull phi4:mini
```

### phi3:mini
- **Size**: ~2GB
- **Speed**: Very fast
- **Quality**: Good
- **Use case**: Lightweight alternative

```powershell
ollama pull phi3:mini
```

### llama2
- **Size**: ~4GB
- **Speed**: Medium
- **Quality**: Very good
- **Use case**: Better reasoning

```powershell
ollama pull llama2
```

### mistral
- **Size**: ~4GB
- **Speed**: Medium
- **Quality**: Excellent
- **Use case**: Complex tasks

```powershell
ollama pull mistral
```

### llama2:13b
- **Size**: ~7GB
- **Speed**: Slower
- **Quality**: Best
- **Use case**: Maximum accuracy (requires more RAM)

```powershell
ollama pull llama2:13b
```

## Using with C2 Server

1. Start the C2 server:
   ```powershell
   python python\c2server.py
   ```

2. Open web interface: http://localhost:5000

3. Navigate to "AI Assistant" tab

4. Configuration:
   - **Model**: `phi4:mini` (or your preferred model)
   - **Ollama URL**: `http://localhost:11434` (default)

5. Click "Initialize Model"

6. Enter natural language objectives and generate attacks!

## Troubleshooting

### "Cannot connect to Ollama"

Check if Ollama is running:
```powershell
curl http://localhost:11434/api/tags
```

Start if needed:
```powershell
ollama serve
```

### "Model not found"

Pull the model first:
```powershell
ollama pull phi4:mini
```

Check installed models:
```powershell
ollama list
```

### Slow generation

- Use smaller models (phi3:mini, phi4:mini)
- Close other applications
- Ensure sufficient RAM (8GB+ recommended)

### Port already in use

Change Ollama port:
```powershell
$env:OLLAMA_HOST = "127.0.0.1:11435"
ollama serve
```

Update C2 server URL to match.

## Advanced Configuration

### Custom Ollama Host

If running Ollama on a different machine:

1. Set Ollama to listen on all interfaces:
   ```powershell
   $env:OLLAMA_HOST = "0.0.0.0:11434"
   ollama serve
   ```

2. In C2 web UI, set URL to:
   ```
   http://YOUR_OLLAMA_IP:11434
   ```

### GPU Acceleration

Ollama automatically uses GPU if available (CUDA/Metal).

Check GPU usage:
```powershell
# Windows - open Task Manager, check GPU tab
# Linux
nvidia-smi
```

### Model Management

Delete a model:
```powershell
ollama rm phi4:mini
```

Update a model:
```powershell
ollama pull phi4:mini
```

Show model info:
```powershell
ollama show phi4:mini
```

## Performance Tips

1. **Close unnecessary applications** - LLMs use lots of RAM
2. **Use SSD** - Faster model loading
3. **Start with small models** - phi4:mini is perfect to start
4. **Upgrade if needed** - Use larger models only if necessary
5. **Monitor resources** - Task Manager / htop

## Security Notes

✅ **Advantages**:
- Runs completely local (no data sent to cloud)
- No API keys needed
- No usage limits
- Private and secure

⚠️ **Remember**:
- LLM-generated scripts should be reviewed
- Test in safe environments first
- Use with proper authorization only

## Additional Resources

- Official docs: https://github.com/ollama/ollama
- Model library: https://ollama.ai/library
- Community: https://discord.gg/ollama

## Quick Reference

```powershell
# Install model
ollama pull phi4:mini

# Run interactively
ollama run phi4:mini

# List models
ollama list

# Remove model
ollama rm phi4:mini

# Check service
curl http://localhost:11434/api/tags

# Start service
ollama serve
```

Happy hacking! 🦙
