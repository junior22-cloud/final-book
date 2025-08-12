# 🚀 Railway Environment Setup for WizBook.io

## Required Environment Variables

Set these in your Railway project's **Variables** tab:

### 1. AI Generation (Required)
```bash
EMERGENT_LLM_KEY=your-emergent-key-here
```
- Get from: [Emergent Dashboard](https://dashboard.emergent.com)
- Format: `sk-emergent-xxxxxxxxxxxx`
- Used for AI book generation

### 2. Payment Processing (Required)
```bash
STRIPE_SECRET_KEY=sk_test_xxxxxxxxx
```
- Get from: [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
- Use test key for development: `sk_test_...`
- Use live key for production: `sk_live_...`

### 3. Deployment (Optional)
```bash
DOMAIN=wizbook.io
RAILWAY_ENVIRONMENT=production
```
- `DOMAIN`: Your custom domain (optional)
- `RAILWAY_ENVIRONMENT`: Auto-set by Railway

## 🔧 How to Set Variables in Railway

1. **Open your Railway project**
2. **Go to Variables tab**
3. **Add each variable:**
   - Click "Add Variable"
   - Enter variable name (e.g., `EMERGENT_LLM_KEY`)
   - Enter variable value (e.g., `sk-emergent-abc123...`)
   - Click "Add"

## 🔐 Security Notes

- **Never commit API keys to GitHub**
- **Use test keys for development**
- **Use live keys only for production**
- **Keys are automatically hidden in Railway UI**

## ✅ Verification

After setting variables, your app will:
- ✅ Generate AI books using Emergent LLM
- ✅ Process payments via Stripe
- ✅ Serve PDFs with watermarks
- ✅ Handle rate limiting properly

## 🚨 Troubleshooting

**If AI generation fails:**
- Check EMERGENT_LLM_KEY format
- Verify key has sufficient credits
- App will use fallback content if key is invalid

**If payments fail:**
- Check STRIPE_SECRET_KEY format
- Verify Stripe account is active
- App will use demo mode if key is invalid

## 📋 Sample .env (for local development)

Create `/app/.env` file:
```bash
EMERGENT_LLM_KEY=sk-emergent-your-key-here
STRIPE_SECRET_KEY=sk_test_your-stripe-key-here  
DOMAIN=localhost:8001
```

## 🌐 Frontend URL Update

Don't forget to update the API URL in `wizbook.html`:
```javascript
const API_URL = 'https://your-railway-app.railway.app';
```

---

**Ready to deploy? 🚀**
1. Set environment variables ✅
2. Push to GitHub
3. Railway auto-deploys
4. Update frontend API URL
5. Test everything works!