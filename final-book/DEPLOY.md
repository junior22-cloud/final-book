# 🚀 WizBook.io Deployment Commands

## 1. Initialize Git Repository
```bash
cd final-book
git init
git add .
git commit -m "🚀 WizBook.io - Production Ready"
```

## 2. Push to GitHub
```bash
# Create new repo on GitHub: wizbook-io
git remote add origin https://github.com/YOUR-USERNAME/wizbook-io.git
git branch -M main
git push -u origin main
```

## 3. Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. New Project → Connect GitHub
3. Select: wizbook-io repository
4. Railway auto-detects: Python app with Procfile ✅

## 4. Set Environment Variables
In Railway Dashboard → Variables:
```bash
EMERGENT_LLM_KEY=sk-emergent-your-actual-key
STRIPE_SECRET_KEY=sk_test_your-actual-key  
DOMAIN=wizbook.io
```

## 5. Add Custom Domain
Railway Dashboard → Networking → Custom Domain:
- Domain: `wizbook.io`
- Port: `8001` (auto-detected)

## 6. DNS Configuration
At your domain registrar (Namecheap/Cloudflare):
```bash
CNAME @ → your-app.up.railway.app
CNAME www → your-app.up.railway.app
```

## 7. Test Live Site
```bash
https://wizbook.io
```

**Total deployment time: ~15 minutes** ⚡

## File Structure ✅
```
final-book/                 ← DEPLOY THIS FOLDER
├─ main.py                 ← FastAPI backend
├─ requirements.txt        ← Python deps  
├─ Procfile               ← Railway config
├─ static/
│   └─ wizbook.html       ← Complete frontend
├─ .env                   ← Your API keys
└─ README.md              ← Documentation
```

**Status: 100% READY FOR LAUNCH** 🎉