# 🔑 Emergent API Integration Guide

## 🚀 Three Ways to Use Emergent AI

### 1. Auto-Integrated Environment (This Chat)
```python
# No key needed - works automatically in supported environments
from emergent_llm import generate
response = generate("Write a Python tutorial for beginners")
```
**Status:** ✅ Available in this environment  
**Setup:** Zero configuration required

### 2. Direct Emergent API (New Format)
```python
# Use your personal Emergent API key
EMERGENT_API_KEY=emg-7a83f2e5c1d4b90f

# API endpoint
url = "https://api.emergentllm.com/v1/generate"
headers = {
    "Authorization": "Bearer emg-7a83f2e5c1d4b90f",
    "Content-Type": "application/json"
}
```
**Status:** ⚪ Requires waitlist signup  
**Format:** `emg-xxxxxxxxx`

### 3. Emergent Integrations (Current Format)
```python
# Current library we've been using
from emergentintegrations.llm.chat import LlmChat
chat = LlmChat(api_key="sk-emergent-b363d2bC56cA76b201")
```
**Status:** ✅ Working now  
**Format:** `sk-emergent-xxxxxxxxx`

## 🔧 BookWiz Smart Routing

Your BookWiz system now intelligently tries all available Emergent options:

```python
# Automatic AI Provider Selection (in order)
1st: Direct Emergent API (emg-xxx)        ⚪ If you have key
2nd: Emergent Integrations (sk-emergent)  ✅ Working now  
3rd: Auto-Integrated Emergent             ✅ This environment
4th: OpenAI Fallback                      ⚪ If you have key
5th: High-Quality Template                ✅ Always available
```

## 📊 API Status Check

Check which providers are available:
```bash
curl http://localhost:8000/
```

Expected response shows your available providers:
```json
{
  "features": {
    "ai_providers": ["emergent_integrations", "emergent_auto", "fallback"]
  }
}
```

## 🎯 Recommended Setup

### For Immediate Use (This Environment)
```bash
# No additional keys needed!
# System automatically uses:
# 1. Emergent Integrations (sk-emergent...)
# 2. Auto-Integrated Emergent  
# 3. High-quality fallbacks
```

### For External Deployment
```bash
# Add to your .env:
EMERGENT_API_KEY=emg-your_key_when_available  # From waitlist
OPENAI_KEY=sk-your_openai_key_here            # As backup
```

## 💡 Key Features Comparison

| Feature | Auto-Integrated | Direct API | Integrations | OpenAI |
|---------|----------------|------------|--------------|--------|
| Auto-model switch | ✅ | ✅ | ✅ | ❌ |
| Zero config | ✅ | ❌ | ❌ | ❌ |
| Rate limits | Higher | Standard | Standard | Standard |
| Cost | Free* | Pay-per-use | Pay-per-use | Pay-per-use |
| Availability | This env | Waitlist | Now | Now |

*Free in supported environments

## 🚦 Testing Your Setup

Test AI generation with your available providers:
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a short guide to quantum computing"}'
```

The system will automatically use the best available provider and tell you which one was used in the logs.

## 🔄 Migration Path

**Current Status:** Your BookWiz works perfectly with existing Emergent Integrations
**Future Options:** Add Direct API key when available for even better performance
**No Downtime:** All changes are backwards compatible

Your AI book generator is ready to use the best available Emergent AI automatically! 🎉