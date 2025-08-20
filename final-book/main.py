import os
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import stripe

# Load .env if you have one
load_dotenv()

app = FastAPI()

# Example: Serve static files if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

# Example route
@app.get("/")
def home():
    return {"message": "FastAPI on Railway is live!"}

# Example Stripe endpoint
@app.post("/create-payment-intent")
async def create_payment(amount: int = Form(...)):
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency="usd"
    )
    return {"client_secret": intent.client_secret}

# Ensure proper port for Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)

