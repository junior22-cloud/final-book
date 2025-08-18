from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import stripe
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Stripe with secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Initialize FastAPI app
app = FastAPI()

# Map tiers to Stripe price IDs
PRICE_IDS = {
    "basic": os.getenv("STRIPE_BASIC_PRICE"),
    "pro": os.getenv("STRIPE_PRO_PRICE"),
    "whitelabel": os.getenv("STRIPE_BUSINESS_PRICE")
}

# Test route to make sure backend is running
@app.get("/")
async def root():
    return {"message": "Backend is running!"}

# Endpoint to create Stripe checkout session
@app.post("/api/create-checkout-session")
async def create_checkout_session(request: Request):
    try:
        data = await request.json()
        tier = data.get("tier")
        topic = data.get("topic", "Default Product")

        if tier not in PRICE_IDS:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid tier"})

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": PRICE_IDS[tier],
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:3000/cancel",
            metadata={"topic": topic}
        )

        return {"status": "success", "session_id": checkout_session.id}

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

