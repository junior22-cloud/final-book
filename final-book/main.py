# main.py
"""WizBook.io - Production-ready FastAPI Backend with Stripe + CSP"""

import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import stripe
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color

# Load environment variables
load_dotenv()

# =========================
# 1️⃣ CREATE APP
# =========================
app = FastAPI(title="WizBook Generator", version="1.0")

# =========================
# 2️⃣ ADD CORS MIDDLEWARE
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://wizbook.io", "http://localhost:8001", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# =========================
# 3️⃣ ADD CSP MIDDLEWARE
# =========================
from starlette.middleware.base import BaseHTTPMiddleware

class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://js.stripe.com; "
            "frame-src https://js.stripe.com; "
            "connect-src https://api.stripe.com"
        )
        return response

app.add_middleware(ContentSecurityPolicyMiddleware)

# =========================
# 4️⃣ STRIPE SETUP
# =========================
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")

# Example config (update with your actual Stripe Price IDs)
STRIPE_PRODUCTS = {
    "basic": {"price_id": os.getenv("STRIPE_BASIC_PRICE")},
    "pro": {"price_id": os.getenv("STRIPE_PRO_PRICE")},
    "whitelabel": {"price_id": os.getenv("STRIPE_BUSINESS_PRICE")}
}

# =========================
# 5️⃣ SIMPLE HEALTH CHECK
# =========================
@app.get("/api/")
async def health_check():
    return {"status": "healthy", "app": "WizBook Generator", "timestamp": datetime.now().isoformat()}

# =========================
# 6️⃣ CREATE CHECKOUT SESSION
# =========================
@app.post("/api/create-checkout-session")
async def create_checkout_session(request: Request):
    data = await request.json()
    topic = data.get("topic", "General Book")
    tier = data.get("tier", "pro")

    price_id = STRIPE_PRODUCTS.get(tier, STRIPE_PRODUCTS["pro"])["price_id"]
    if not price_id:
        raise HTTPException(status_code=500, detail="Stripe Price ID not configured")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            success_url=f"https://wizbook.io/success?topic={topic}&tier={tier}",
            cancel_url=f"https://wizbook.io/cancel?topic={topic}",
            metadata={"topic": topic, "tier": tier}
        )
        return {"status": "success", "checkout_url": session.url, "session_id": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================
# 7️⃣ STATIC FILES
# =========================
app.mount("/", StaticFiles(directory="final-book/static", html=True), name="static")

# =========================
# 8️⃣ RUN APP
# =========================
if __name__ == "__main__":
    import uvicorn
    host = "0.0.0.0" if os.getenv("RAILWAY_ENVIRONMENT") else "localhost"
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host=host, port=port)
