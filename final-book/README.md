# 📖 WizBook.io - AI Book Generator

Turn ideas into professional books in 60 seconds!

## 🚀 Quick Deploy to Railway

1. **Clone & Deploy**
   ```bash
   git clone <your-repo>
   cd final-book
   ```

2. **Set Environment Variables**
   ```bash
   EMERGENT_LLM_KEY=sk-emergent-your-key-here
   STRIPE_SECRET_KEY=sk_test_your-stripe-key-here
   DOMAIN=wizbook.io
   ```

3. **Deploy**
   - Push to GitHub
   - Connect to Railway
   - Add custom domain: wizbook.io

## 📁 Project Structure

```
final-book/
├─ main.py              # FastAPI backend
├─ requirements.txt     # Python dependencies  
├─ Procfile            # Railway deployment config
├─ static/
│   └─ wizbook.html    # Complete frontend (React + HTML)
├─ templates/          # Optional Jinja2 templates
├─ .env               # Environment variables
└─ README.md          # This file
```

## ✨ Features

- 🤖 **AI Book Generation** - Multiple AI providers with fallbacks
- 📄 **PDF Export** - Professional watermarked PDFs
- 💳 **Stripe Payments** - $9.99 per book with secure checkout
- 🎨 **Modern UI** - Clean, responsive design
- ⚡ **Ultra Fast** - Single-file deployment

## 🔧 Local Development

```bash
pip install -r requirements.txt
python main.py
# Visit: http://localhost:8001
```

## 🌐 API Endpoints

- `GET /api/generate?topic=Python` - Generate AI book
- `GET /api/pdf?topic=Python` - Download PDF
- `GET /api/checkout?topic=Python` - Stripe payment

## 📝 License

Built with ❤️ for entrepreneurs and content creators.