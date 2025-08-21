# main.py
"""WizBook.io - Production-Grade Backend with Stripe & Emergent AI Integration"""

import os
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import stripe
from jose import JWTError, jwt
from passlib.context import CryptContext
import httpx

# =========================
# 0️⃣ CONFIGURATION & LIFECYCLE
# =========================
# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Security scheme for API protection
security = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 WizBook.io Backend Initializing...")
    logger.info(f"📍 Domain: {os.getenv('DOMAIN', 'localhost')}")
    logger.info(f"💰 Stripe Mode: {'LIVE' if 'sk_live' in os.getenv('STRIPE_SECRET_KEY', '') else 'TEST'}")
    logger.info(f"🧠 Emergent AI: {'CONFIGURED' if os.getenv('EMERGENT_LLM_KEY') else 'DISABLED'}")
    
    # Validate critical configuration
    required_vars = ['STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY', 'JWT_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"❌ Missing critical environment variables: {missing_vars}")
    
    yield
    
    # Shutdown
    logger.info("🛑 WizBook.io Backend Shutting Down...")

# =========================
# 1️⃣ CREATE APP WITH LIFECYCLE
# =========================
app = FastAPI(
    title=os.getenv("APP_NAME", "WizBook Generator API"),
    description="Professional AI-powered book generation service with Stripe payments",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    servers=[{"url": f"https://{os.getenv('DOMAIN', 'localhost')}", "description": "Production server"}]
)

# Configure CORS from environment variable
cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 2️⃣ SECURITY MIDDLEWARE
# =========================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        response.headers.update({
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://js.stripe.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https: blob:; "
                "frame-src https://js.stripe.com; "
                "connect-src 'self' https://api.stripe.com https://api.emergent.ai; "
                "form-action 'self'; "
                "base-uri 'self'; "
                "frame-ancestors 'self';"
            ),
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "payment=()",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        })
        return response

app.add_middleware(SecurityHeadersMiddleware)

# =========================
# 3️⃣ STRIPE CONFIGURATION
# =========================
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe.api_version = "2024-06-20"

STRIPE_PRODUCTS = {
    "basic": {
        "price_id": os.getenv("STRIPE_BASIC_PRICE"),
        "name": "Basic Book Package",
        "price": 47,
        "features": ["100 pages", "Basic formatting", "PDF export"]
    },
    "pro": {
        "price_id": os.getenv("STRIPE_PRO_PRICE"),
        "name": "Professional Package", 
        "price": 97,
        "features": ["300 pages", "Advanced formatting", "PDF+EPUB export", "Illustrations"]
    },
    "business": {
        "price_id": os.getenv("STRIPE_BUSINESS_PRICE"),
        "name": "White Label Solution",
        "price": 497,
        "features": ["Unlimited pages", "White labeling", "Custom branding", "Priority support"]
    }
}

# =========================
# 4️⃣ EMERGENT AI INTEGRATION
# =========================
class EmergentAI:
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        self.base_url = "https://api.emergent.ai/v1"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def generate_content(self, prompt: str, model: str = "emergent-ultra") -> Optional[Dict]:
        if not self.api_key:
            logger.warning("Emergent AI API key not configured")
            return None
            
        try:
            response = await self.client.post(
                f"{self.base_url}/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model,
                    "prompt": prompt,
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Emergent AI error: {str(e)}")
            return None

emergent_ai = EmergentAI()

# =========================
# 5️⃣ AUTH & SECURITY HELPERS
# =========================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> bool:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    expected_key = os.getenv("API_KEY")
    if credentials.credentials != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return True

def validate_tier(tier: str) -> str:
    return tier if tier in STRIPE_PRODUCTS else "pro"

# =========================
# 6️⃣ API ROUTES
# =========================
@app.get("/")
async def root():
    return {
        "service": os.getenv("APP_NAME", "WizBook Generator"),
        "version": "3.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/api/health",
            "products": "/api/products",
            "checkout": "/api/create-checkout-session",
            "docs": "/api/docs"
        }
    }

@app.get("/api/health")
async def health_check():
    """Comprehensive system health check"""
    stripe_configured = bool(stripe.api_key and "sk_" in stripe.api_key)
    emergent_configured = bool(os.getenv("EMERGENT_LLM_KEY"))
    
    price_configuration = {
        tier: bool(STRIPE_PRODUCTS[tier]["price_id"])
        for tier in STRIPE_PRODUCTS
    }
    
    return {
        "status": "healthy" if all(price_configuration.values()) and stripe_configured else "degraded",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "stripe": stripe_configured,
            "emergent_ai": emergent_configured,
            "price_configuration": price_configuration,
            "api": True
        },
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "domain": os.getenv("DOMAIN", "localhost")
    }

@app.post("/api/create-checkout-session")
async def create_checkout_session(request: Request, authorized: bool = Depends(verify_api_key)):
    """Create Stripe checkout session"""
    try:
        data = await request.json()
        topic = data.get("topic", "").strip()
        tier = validate_tier(data.get("tier", "pro"))
        
        if not topic or len(topic) > 200:
            raise HTTPException(status_code=400, detail="Topic must be between 1-200 characters")
        
        price_id = STRIPE_PRODUCTS[tier]["price_id"]
        if not price_id or not price_id.startswith("price_"):
            raise HTTPException(status_code=500, detail="Payment system not configured")
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
                "adjustable_quantity": {"enabled": False}
            }],
            mode="payment",
            success_url=f"https://{os.getenv('DOMAIN')}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"https://{os.getenv('DOMAIN')}/cancel",
            customer_creation="if_required",
            metadata={
                "topic": topic[:100],
                "tier": tier,
                "project_id": f"wizbook_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            },
            allow_promotion_codes=True,
            billing_address_collection="required",
            shipping_address_collection={"allowed_countries": ["US", "CA", "GB", "AU"]},
            phone_number_collection={"enabled": True}
        )
        
        logger.info(f"💰 Checkout session created for {tier} tier: {session.id}")
        
        return JSONResponse(status_code=200, content={
            "status": "success",
            "checkout_url": session.url,
            "session_id": session.id,
            "expires_at": session.expires_at,
            "tier": tier,
            "price": STRIPE_PRODUCTS[tier]["price"]
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment processing error")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/products")
async def get_products(authorized: bool = Depends(verify_api_key)):
    """Get available products and pricing"""
    return {
        "products": {
            tier: {
                "name": info["name"],
                "price": info["price"],
                "currency": "usd",
                "features": info["features"],
                "price_id": info["price_id"]
            }
            for tier, info in STRIPE_PRODUCTS.items()
        }
    }

@app.post("/api/generate-content")
async def generate_content(request: Request, authorized: bool = Depends(verify_api_key)):
    """Generate content using Emergent AI"""
    try:
        data = await request.json()
        prompt = data.get("prompt", "").strip()
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        result = await emergent_ai.generate_content(prompt)
        if not result:
            raise HTTPException(status_code=503, detail="AI service unavailable")
        
        return {
            "status": "success",
            "content": result.get("choices", [{}])[0].get("text", ""),
            "model": result.get("model", "emergent-ultra")
        }
        
    except Exception as e:
        logger.error(f"Content generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Content generation failed")

@app.post("/api/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("WEBHOOK_SECRET")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle checkout completion
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"✅ Payment completed: {session.id}")
        # TODO: Trigger book generation process
    
    return {"status": "success"}

# =========================
# 7️⃣ STATIC FILES SERVING
# =========================
static_dir = "static"
if os.path.exists(static_dir) and os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    logger.info(f"📁 Serving static files from: {static_dir}")
else:
    logger.warning("⚠️ Static directory not found - API mode only")

# =========================
# 8️⃣ ERROR HANDLING
# =========================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )

# =========================
# 9️⃣ PERFORMANCE MIDDLEWARE
# =========================
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    response.headers["X-Response-Time"] = f"{process_time:.3f}s"
    return response

# =========================
# 🔟 MAIN EXECUTION (DEV ONLY)
# =========================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info",
        timeout_keep_alive=60,
        proxy_headers=True
    )
