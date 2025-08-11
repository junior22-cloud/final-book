# 🔧 Complete Environment Setup Guide

## 📋 Environment Variables Checklist

### Required for Basic Operation
- [x] `EMERGENT_LLM_KEY` - Multi-model AI (included)
- [ ] `STRIPE_SECRET_KEY` - Payment processing (required)

### Optional Enhancements
- [ ] `OPENAI_KEY` - Direct OpenAI integration
- [ ] `NEXT_PUBLIC_SUPABASE_URL` - User management & book storage
- [ ] `NEXT_PUBLIC_SUPABASE_KEY` - Supabase authentication

## 🚀 Quick Setup (5 Minutes)

### 1. Basic Setup (Stripe Only)
```bash
# Backend .env
EMERGENT_LLM_KEY=sk-emergent-b363d2bC56cA76b201
STRIPE_SECRET_KEY=sk_your_stripe_secret_key_here

# Frontend .env.local  
NEXT_PUBLIC_STRIPE_KEY=pk_your_stripe_publishable_key_here
```

### 2. Enhanced Setup (All Services)
```bash
# Backend .env
EMERGENT_LLM_KEY=sk-emergent-b363d2bC56cA76b201
OPENAI_KEY=sk-your_openai_api_key_here
STRIPE_SECRET_KEY=sk_your_stripe_secret_key_here
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# Frontend .env.local
NEXT_PUBLIC_STRIPE_KEY=pk_your_stripe_publishable_key_here
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_KEY=your_supabase_anon_key_here
```

## 🔑 How to Get Each API Key

### 1. Stripe (Required)
1. Go to [stripe.com](https://stripe.com) → Sign up
2. Dashboard → Developers → API Keys
3. Copy both **Publishable** and **Secret** keys
4. **Cost:** Free for testing, 2.9% + 30¢ per transaction

### 2. OpenAI (Optional)
1. Go to [platform.openai.com](https://platform.openai.com)
2. API Keys → Create new secret key
3. **Cost:** ~$0.002 per 1K tokens (very affordable)
4. **Benefit:** Direct OpenAI access as backup to Emergent LLM

### 3. Supabase (Optional)
1. Go to [supabase.com](https://supabase.com) → New project
2. Settings → API → Copy URL and anon key
3. **Cost:** Free for 50K monthly active users
4. **Benefit:** User accounts, book storage, real database

## 🏗️ Service Architecture

### AI Generation (Tiered Approach)
```
1st: Emergent LLM (gpt-4o-mini) ✅ Working
2nd: OpenAI (gpt-3.5-turbo) ⚪ Optional  
3rd: High-quality fallback ✅ Always available
```

### Data Storage Options
```
Current: In-memory (demo mode) ✅
Enhanced: MongoDB (local) ⚪ Basic persistence
Premium: Supabase (cloud) ⚪ Full user management
```

### Payment Processing
```
Stripe: Production-ready ✅
Rate Limited: 5/minute ✅
Watermarked PDFs: Included ✅
```

## 🎯 Recommended Setup Paths

### Path 1: Quick Launch (Revenue Focus)
**Time:** 10 minutes  
**Services:** Emergent LLM + Stripe  
**Result:** Immediate revenue generation  

```bash
# Just add your Stripe keys and launch!
STRIPE_SECRET_KEY=sk_...
NEXT_PUBLIC_STRIPE_KEY=pk_...
```

### Path 2: Enhanced Quality (AI Focus)
**Time:** 15 minutes  
**Services:** Emergent LLM + OpenAI + Stripe  
**Result:** Higher AI reliability, better content  

```bash
# Add OpenAI as backup AI service
OPENAI_KEY=sk-...
STRIPE_SECRET_KEY=sk_...
```

### Path 3: Full Platform (User Focus)
**Time:** 30 minutes  
**Services:** All services integrated  
**Result:** Complete SaaS platform with user accounts  

```bash
# Full-featured platform
OPENAI_KEY=sk-...
STRIPE_SECRET_KEY=sk_...
NEXT_PUBLIC_SUPABASE_URL=https://...
NEXT_PUBLIC_SUPABASE_KEY=eyJ...
```

## 🧪 Testing Each Service

### Test Stripe
```bash
curl -X POST "http://localhost:8000/api/checkout" \
  -H "Content-Type: application/json" \
  -d '{}'
# Should return: {"id": "cs_..."}
```

### Test AI Generation
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a short story"}'
# Should return quality content
```

### Test PDF Export
```bash
# Generate content first, then:
curl -X POST "http://localhost:8000/api/export" \
  -H "Content-Type: application/json" \
  -d '{"text": "# Test\n\nContent here"}' \
  --output test.pdf
# Should create watermarked PDF
```

## 📊 Service Status Dashboard

Check your setup status:
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "BookWiz Generator API",
  "status": "ready",
  "features": {
    "ai_providers": ["emergent_llm", "openai"],
    "database": "mongodb", 
    "auth": "supabase",
    "payments": "stripe",
    "watermarking": "enabled"
  }
}
```

## 🚨 Troubleshooting

### Issue: "Invalid API Key"
**Solution:** Double-check key format and permissions

### Issue: Rate limits too strict
**Solution:** Adjust in environment variables:
```bash
RATE_LIMIT_GENERATION=20  # Increase from 10
RATE_LIMIT_EXPORT=50      # Increase from 20
```

### Issue: AI generation fails
**Solution:** System automatically falls back:
1. Emergent LLM → 2. OpenAI → 3. High-quality template

### Issue: Supabase not working
**Solution:** Supabase is optional - system works without it

## 💰 Cost Breakdown

### Minimal Setup (Stripe only)
- **Hosting:** $5-20/month
- **Stripe:** 2.9% + 30¢ per sale
- **Total:** ~$5/month + transaction fees

### Enhanced Setup (+ OpenAI)
- **Above costs +**
- **OpenAI:** ~$1-10/month (depending on usage)
- **Total:** ~$6-30/month + transaction fees

### Full Setup (+ Supabase)  
- **Above costs +**
- **Supabase:** Free up to 50K users
- **Total:** ~$6-30/month + transaction fees

## 🎉 Ready to Launch

Once your environment is configured:

1. **Start Backend:** `python working_backend.py`
2. **Start Frontend:** `npm start` 
3. **Test Complete Flow:** Generate → Pay → Download PDF
4. **Go Live:** Replace test keys with production keys

Your BookWiz Generator is now ready for production! 🚀