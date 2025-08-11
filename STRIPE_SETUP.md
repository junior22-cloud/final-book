# 🔑 REPLACE THESE WITH YOUR REAL STRIPE KEYS

# Backend (.env file) - Replace the placeholder:
STRIPE_SECRET_KEY=sk_test_51234567890abcdef_YOUR_REAL_SECRET_KEY_HERE

# Frontend (.env.local file) - Add this:  
NEXT_PUBLIC_STRIPE_KEY=pk_test_51234567890abcdef_YOUR_REAL_PUBLISHABLE_KEY_HERE

# Where to get these keys:
# 1. Login to stripe.com
# 2. Go to Developers → API Keys
# 3. Copy "Publishable key" and "Secret key"
# 4. Paste them in the files above
# 5. Restart your backend: python working_backend.py