#!/bin/bash
# Railway Quick Deploy Script

echo "🚄 BookWiz Railway Deployment Script"
echo "====================================="

# Check if files exist
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found. Please run from the correct directory."
    exit 1
fi

echo "✅ Files found:"
echo "   - main.py ($(wc -l < main.py) lines)"
echo "   - requirements.txt ($(wc -l < requirements.txt) packages)"
echo "   - index.html ($(wc -c < index.html) bytes)"

echo ""
echo "📋 Railway Deployment Checklist:"
echo ""
echo "1. Go to railway.app and sign up"
echo "2. Click 'Deploy from GitHub' or 'Deploy from folder'"
echo "3. Upload these files:"
echo "   ✅ main.py"
echo "   ✅ requirements.txt" 
echo "   ✅ Procfile"
echo ""
echo "4. In Railway Settings, add these commands:"
echo ""
echo "BUILD COMMAND:"
echo "echo 'Private networking not required' && pip install -r requirements.txt"
echo ""
echo "START COMMAND:" 
echo "python main.py --host 0.0.0.0 --port \$PORT"
echo ""
echo "ENVIRONMENT VARIABLES:"
echo "EMERGENT_LLM_KEY=sk-emergent-b363d2bC56cA76b201"
echo "STRIPE_SECRET_KEY=your_stripe_key_here"
echo "RAILWAY_ENVIRONMENT=production"
echo ""
echo "5. Deploy and get your Railway URL"
echo "6. Update index.html with your Railway URL"  
echo "7. Deploy index.html to Netlify"
echo ""
echo "🎉 Your BookWiz will be live in 10 minutes!"
echo ""
echo "Test your deployment:"
echo "curl 'https://your-railway-app.railway.app/generate?topic=Python'"