# 🚀 EMERGENT DEPLOYMENT PACKAGE - WizBook.io

## 📂 STEP 1: CORRECT CODE EXTRACTED

### ✅ main.py (Complete FastAPI Backend)
✅ handleCheckout() function with real Stripe integration
✅ AI book generation with EMERGENT_LLM_KEY
✅ PDF generation with watermarking
✅ Email capture system
✅ Static file serving for frontend

### ✅ requirements.txt (Emergent-Compatible)
```
fastapi>=0.110.1
uvicorn>=0.25.0
python-dotenv>=1.0.1
emergentintegrations
python-multipart>=0.0.9
reportlab>=4.0.0
stripe>=5.0.0
```

### ✅ static/index.html (Frontend with handleCheckout)
✅ Clean handleCheckout() function
✅ All pricing cards using handleCheckout(topic, tier)
✅ Professional UI with countdown timer
✅ Email capture popup

## 🔧 STEP 2: EMERGENT ENVIRONMENT VARIABLES

Set these in Emergent:
```
EMERGENT_LLM_KEY=sk-emergent-1Bd1aE8F1A28bD7B9A
STRIPE_SECRET_KEY=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
DOMAIN=wizbook.io
```

## 🎯 STEP 3: DEPLOYMENT CHECKLIST

1. ✅ Copy main.py to Emergent backend editor
2. ✅ Copy requirements.txt to Emergent
3. ✅ Set environment variables in Emergent dashboard
4. ✅ Deploy and test
5. ✅ Verify real Stripe checkout works

## 🧪 STEP 4: TESTING

Test URL: https://your-emergent-app.com/api/checkout?topic=TEST&tier=pro
Expected: Redirect to REAL Stripe checkout (not demo mode)

Buttons: All pricing cards should call handleCheckout() and redirect to Stripe