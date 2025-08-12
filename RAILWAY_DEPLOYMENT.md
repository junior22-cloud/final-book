# 🚀 WizBook.io Railway Deployment Guide

## 1. FRONTEND (HTML) ✅ - COMPLETE

The frontend has been simplified to a single HTML file served directly from FastAPI:

```
/app/frontend/static/index.html  ← Complete WizBook.io frontend
```

## 2. BACKEND (FastAPI) ✅ - COMPLETE  

Updated `main.py` to serve static files:

```python
# Added to main.py
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend/static", html=True), name="static")
```

**API Endpoints:**
- `GET /api/generate?topic=...` - Generate book
- `GET /api/pdf?topic=...` - Download PDF  
- `GET /api/checkout?topic=...` - Stripe payment

## 3. RAILWAY SETUP

### Step 1: GitHub Repository
```bash
# Push your code to GitHub
git add .
git commit -m "WizBook.io deployment ready"
git push origin main
```

### Step 2: Railway Project
1. **Connect GitHub:** Go to [railway.app](https://railway.app) → New Project → GitHub
2. **Select Repository:** Choose your WizBook.io repo
3. **Configure Build:**
   - **Build Command:** `echo 'Skipping build for HTML app'`
   - **Start Command:** `python main.py`

### Step 3: Environment Variables
In Railway → Variables tab, add:

```bash
EMERGENT_LLM_KEY=sk-emergent-your-key-here
STRIPE_SECRET_KEY=sk_test_your-stripe-key-here  
DOMAIN=wizbook.io
```

### Step 4: Update Frontend URL
In `/app/frontend/static/index.html`, replace:
```javascript
// Change this line:
const API_URL = 'https://YOUR-RAILWAY-APP.up.railway.app';

// To your actual Railway URL:
const API_URL = 'https://wizbook-production.up.railway.app';
```

## 4. DOMAIN CONNECTION 🌐

### Option A: Buy Domain + Connect to Railway
1. **Buy wizbook.io** on Namecheap/GoDaddy
2. **In Railway:** Settings → Domains → Add Custom Domain → `wizbook.io`
3. **In Domain Provider:** Add CNAME record:
   ```
   CNAME @ → your-app.up.railway.app
   ```

### Option B: Use Railway Subdomain
Railway gives you a free subdomain like:
```
https://wizbook-production.up.railway.app
```

## 5. TESTING DEPLOYMENT

After deployment, test these endpoints:
- `https://your-app.railway.app/` - Should load WizBook.io homepage
- `https://your-app.railway.app/api/generate?topic=Test` - Should generate book
- `https://your-app.railway.app/api/pdf?topic=Test` - Should download PDF

## 6. FILE STRUCTURE ✅

Your final structure should be:
```
/app/
├── main.py                    # FastAPI backend with static file serving
├── frontend/
│   └── static/
│       └── index.html         # Complete WizBook.io frontend
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── RAILWAY_DEPLOYMENT.md     # This file
```

## 7. TROUBLESHOOTING

**If AI generation fails:**
- Check `EMERGENT_LLM_KEY` is set correctly
- App will use fallback content if key is invalid

**If payments fail:**  
- Check `STRIPE_SECRET_KEY` is set correctly
- App will use demo mode if key is invalid

**If frontend doesn't load:**
- Verify `/frontend/static/index.html` exists
- Check Railway build logs for errors

## 8. NEXT STEPS

1. ✅ Push to GitHub
2. ✅ Deploy to Railway  
3. ✅ Set environment variables
4. ✅ Update frontend API URL
5. 🌐 Connect custom domain (optional)
6. 🧪 Test all features work

**Ready to go live! 🎉**