# OpenRouter Setup Guide

OpenRouter provides access to multiple AI models through a unified API, including free models perfect for generating Ducky scripts.

## What is OpenRouter?

OpenRouter is a unified API gateway that provides access to various LLM providers (OpenAI, Anthropic, Google, Meta, Mistral, etc.) through a single interface. They offer free tier access to several models.

## Why Use OpenRouter?

**Advantages:**
- No local installation required
- Access to powerful cloud models
- Free tier with generous limits
- No GPU/RAM requirements
- Works from any device with internet

**Disadvantages:**
- Requires internet connection
- Data sent to cloud (less private than Ollama)
- Rate limits on free tier
- Requires API key management

## Setup Steps

### 1. Create Account

1. Go to https://openrouter.ai
2. Click "Sign Up" or "Log In"
3. Sign up with GitHub, Google, or email

### 2. Get API Key

1. Navigate to https://openrouter.ai/keys
2. Click "Create Key"
3. Give it a name (e.g., "C2 Server")
4. Copy the key (starts with `sk-or-v1-`)
5. **Important:** Save it securely - you won't be able to see it again!

### 3. Add Credits (Optional)

The free tier includes:
- Some models are completely free (devstral-small-2505)
- $5 free credits for new users
- Rate limits apply

To add more credits:
1. Go to https://openrouter.ai/credits
2. Click "Add Credits"
3. Choose amount and payment method

## Recommended Models

### Free Models (No Credits Required)

**devstral-small-2505** (Recommended for Ducky Scripts)
- Completely free forever
- Optimized for code generation
- Fast responses
- Perfect for generating Ducky scripts

**google/gemini-flash-1.5-8b**
- Free tier available
- Very fast responses
- Good for simple tasks

### Paid Models (Low Cost)

**openai/gpt-4o-mini**
- $0.15 per 1M input tokens
- $0.60 per 1M output tokens
- Very capable for complex scripts

**anthropic/claude-3-haiku**
- $0.25 per 1M input tokens
- $1.25 per 1M output tokens
- Excellent at following instructions

## Using with C2 Server

### Web Interface

1. Open http://localhost:5000
2. Go to "AI Assistant" tab
3. Check "Enable AI Assistant"
4. Select **OpenRouter** from Provider dropdown
5. Enter model name: `devstral-small-2505`
6. Enter your API key
7. Click "Initialize Model"
8. Enter your attack objective
9. Click "Generate & Execute Attack"

### Example Configuration

```
Provider: OpenRouter (Cloud)
Model: devstral-small-2505
API Key: sk-or-v1-... (your key here)
```

## Troubleshooting

### "Cannot connect to OpenRouter"
- Check internet connection
- Verify API key is correct
- Try again in a few seconds (rate limiting)

### "Invalid API Key"
- Ensure you copied the full key including `sk-or-v1-` prefix
- Key might have expired - create a new one
- Check for extra spaces when pasting

### "Insufficient credits"
- Free model (devstral-small-2505) should not require credits
- Check your balance at https://openrouter.ai/credits
- Add credits if using paid models

### "Rate limit exceeded"
- Free tier has rate limits
- Wait a minute and try again
- Consider upgrading for higher limits

### Model not found
- Verify model name is correct
- Check available models at https://openrouter.ai/models
- Some models may be temporarily unavailable

## Model Comparison

| Model | Cost | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| devstral-small-2505 | **Free** | Fast | Good | **Ducky scripts (recommended)** |
| google/gemini-flash-1.5-8b | Free* | Very Fast | Good | Simple scripts |
| openai/gpt-4o-mini | Low | Fast | Excellent | Complex logic |
| anthropic/claude-3-haiku | Low | Fast | Excellent | Creative scripts |

*Subject to rate limits

## Privacy Considerations

⚠️ **Important:** When using OpenRouter, your prompts and generated scripts are sent to cloud servers.

**What OpenRouter sees:**
- Your attack objectives
- Generated Ducky scripts
- Model usage patterns

**What OpenRouter does NOT see:**
- Your target's data
- Actual execution results
- Your network topology

**Recommendations:**
- Use generic objectives when testing
- Avoid including sensitive details in prompts
- For maximum privacy, use Ollama (local) instead
- Review OpenRouter's privacy policy at https://openrouter.ai/privacy

## API Key Security

### Best Practices

1. **Never share your API key**
   - Don't commit to git
   - Don't post in forums/Discord
   - Don't email or message

2. **Rotate regularly**
   - Create new keys periodically
   - Delete old unused keys

3. **Use environment variables (optional)**
   ```powershell
   # PowerShell
   $env:OPENROUTER_API_KEY="sk-or-v1-..."
   
   # Then read in Python code if implementing
   import os
   api_key = os.getenv('OPENROUTER_API_KEY')
   ```

4. **Monitor usage**
   - Check https://openrouter.ai/activity regularly
   - Set up spending limits if using paid models

### If Your Key is Compromised

1. Immediately delete the key at https://openrouter.ai/keys
2. Create a new key
3. Update your C2 server configuration
4. Check activity logs for unauthorized usage

## Advanced Usage

### Testing with curl

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "devstral-small-2505",
    "messages": [
      {"role": "user", "content": "Generate a Ducky script to open calculator"}
    ]
  }'
```

### Rate Limits

Free tier limits (as of 2025):
- 10 requests per minute
- 100 requests per day
- Varies by model

Paid tier:
- Much higher limits
- Priority processing
- No daily caps

## FAQ

**Q: Is devstral-small-2505 really free forever?**
A: Yes, this model is provided completely free through OpenRouter.

**Q: Can I use multiple models?**
A: Yes, just change the model name in the web interface and reinitialize.

**Q: Do I need a credit card for free models?**
A: No, free models require no payment method.

**Q: How do I see my usage?**
A: Check https://openrouter.ai/activity for detailed usage statistics.

**Q: Can I use this for commercial projects?**
A: Check OpenRouter's terms of service. Free tier is typically for development/testing.

**Q: Which is better: Ollama or OpenRouter?**
A: 
- **Ollama**: Better privacy, faster (no network latency), offline capable, requires good hardware
- **OpenRouter**: No hardware requirements, access to many models, requires internet, less private

## Getting Help

- OpenRouter Documentation: https://openrouter.ai/docs
- OpenRouter Discord: https://discord.gg/openrouter
- Model Rankings: https://openrouter.ai/rankings
- Status Page: https://status.openrouter.ai

## Quick Reference

```yaml
# Free Model Configuration
Provider: OpenRouter (Cloud)
Model: devstral-small-2505
API Key: sk-or-v1-[YOUR-KEY-HERE]
Website: https://openrouter.ai
Docs: https://openrouter.ai/docs
```

---

**Ready to use?** Get your free API key at https://openrouter.ai/keys and start generating Ducky scripts with AI! 🚀
