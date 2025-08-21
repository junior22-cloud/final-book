"""
WizBook.io - Production API with Stripe & Emergent AI
Deployment: Railway
Frontend: Static Files
Author: Your Full-Stack Engineer
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer
import stripe
from jose import JWTError, jwt
from passlib.context import CryptContext
import httpx

# ===================== CONFIGURATION =====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe.api_version = "2024-06-20"

# Security
security = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Product Configuration
STRIPE_PRODUCTS = {
    "basic": {
        "price_id": os.getenv("STRIPE_BASIC_PRICE"),
        "name": "Basic Package",
        "price": 47,
        "features": ["100 pages", "Basic formatting", "PDF export"]
    },
    "pro": {
        "price_id": os.getenv("STRIPE_PRO_PRICE"), 
        "name": "Professional Package", 
        "price": 97,
        "features": ["300 pages", "Advanced formatting", "PDF+EPUB export"]
    },
    "business": {
        "price_id": os.getenv("STRIPE_BUSINESS_PRICE"),
        "name": "Business Package",
        "price": 497,
        "features": ["Unlimited pages", "White labeling", "Priority support"]
    }
}

# ===================== APP INITIALIZATION =====================
app = FastAPI(
    title="WizBook Generator API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== EMERGENT AI CLIENT =====================
class EmergentAI:
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        self.base_url = "https://api.emergent.ai/v1"
    
    async def generate_content(self, prompt: str) -> Optional[Dict]:
        if not self.api_key:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "emergent-ultra",
                        "prompt": prompt,
                        "max_tokens": 2000,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Emergent AI error: {str(e)}")
            return None

emergent_ai = EmergentAI()

# ===================== AUTH HELPERS =====================
async def verify_api_key(credentials: Optional[HTTPBearer] = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing API key")
    
    expected_key = os.getenv("API_KEY")
    if credentials.credentials != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True

# ===================== API ROUTES =====================
@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "WizBook Generator API"
    }

@app.get("/api/products")
async def get_products(authorized: bool = Depends(verify_api_key)):
    return {"products": STRIPE_PRODUCTS}

@app.post("/api/create-checkout-session")
async def create_checkout_session(request: Request, authorized: bool = Depends(verify_api_key)):
    try:
        data = await request.json()
        tier = data.get("tier", "pro")
        
        if tier not in STRIPE_PRODUCTS:
            raise HTTPException(status_code=400, detail="Invalid tier")
        
        price_id = STRIPE_PRODUCTS[tier]["price_id"]
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            success_url=f"https://{os.getenv('DOMAIN')}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"https://{os.getenv('DOMAIN')}/cancel",
            metadata={"tier": tier}
        )
        
        return JSONResponse({
            "checkout_url": session.url,
            "session_id": session.id
        })
        
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Checkout creation failed")

@app.post("/api/generate-content")
async def generate_content(request: Request, authorized: bool = Depends(verify_api_key)):
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt required")
        
        result = await emergent_ai.generate_content(prompt)
        
        if not result:
            raise HTTPException(status_code=503, detail="AI service unavailable")
        
        return {
            "content": result.get("choices", [{}])[0].get("text", ""),
            "model": result.get("model", "emergent-ultra")
        }
        
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Content generation failed")

@app.post("/api/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("WEBHOOK_SECRET")
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook")
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"Payment completed: {session.id}")
        # TODO: Trigger book generation
    
    return {"status": "success"}

# ===================== STATIC FILES =====================
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# ===================== ERROR HANDLING =====================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
