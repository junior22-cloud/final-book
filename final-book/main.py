# main.py
"""WizBook.io - Production-ready Backend with Stripe Integration"""

import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
import stripe
import logging
from typing import Optional

# =========================
# 0️⃣ CONFIGURATION & LIFECYCLE
# =========================
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security scheme for API protection
security = HTTPBearer(auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting WizBook.io Backend")
    logger.info(f"✅ Stripe Mode: {'LIVE' if 'sk_live' in os.getenv('STRIPE_SECRET_KEY', '') else 'TEST'}")
    yield
    # Shutdown
    logger.info("🛑 Shutting down WizBook.io Backend")

# =========================
# 1️⃣ CREATE APP WITH LIFECYCLE
# =========================
app = FastAPI(
    title="WizBook Generator API",
    description="Professional book generation service with Stripe payments",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://wizbook.io",
        "https://www.wizbook.io",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://*.up.railway.app",
        os.getenv("RAILWAY_STATIC_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 2️⃣ SECURITY & CSP MIDDLEWARE
# =========================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers.update({
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://js.stripe.com; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "frame-src https://js.stripe.com; "
                "connect-src 'self' https://api.stripe.com; "
                "form-action 'self'; "
                "base-uri 'self'; "
                "frame-ancestors 'self';"
            ),
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "payment=()"
        })
        return response

app.add_middleware(SecurityHeadersMiddleware)

# =========================
# 3️⃣ STRIPE CONFIGURATION
# =========================
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe.api_version = "2024-06-20"

# Validate Stripe configuration
if not stripe.api_key or "sk_" not in stripe.api_key:
    logger.warning("⚠️ Stripe secret key not configured properly")

STRIPE_PRODUCTS = {
    "basic": {
        "price_id": os.getenv("STRIPE_BASIC_PRICE", "price_basic_placeholder"),
        "name": "Basic Book Package",
        "price": 19
    },
    "pro": {
        "price_id": os.getenv("STRIPE_PRO_PRICE", "price_pro_placeholder"),
        "name": "Professional Package", 
        "price": 49
    },
    "whitelabel": {
        "price_id": os.getenv("STRIPE_BUSINESS_PRICE", "price_business_placeholder"),
        "name": "White Label Solution",
        "price": 199
    }
}

# =========================
# 4️⃣ DEPENDENCIES & HELPERS
# =========================
async def verify_api_key(authorization: Optional[HTTPBearer] = Depends(security)):
    """Validate API key for sensitive endpoints"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")
    
    expected_key = os.getenv("API_KEY")
    if authorization.credentials != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True

def validate_tier(tier: str) -> str:
    """Validate and normalize tier selection"""
    tier = tier.lower()
    if tier not in STRIPE_PRODUCTS:
        tier = "pro"
    return tier

# =========================
# 5️⃣ API ROUTES
# =========================
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "WizBook Generator API",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/api/health",
            "checkout": "/api/create-checkout-session",
            "docs": "/api/docs"
        }
    }

@app.get("/api/health")
async def health_check():
    """Comprehensive health check endpoint"""
    stripe_healthy = bool(stripe.api_key and "sk_" in stripe.api_key)
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "stripe": stripe_healthy,
            "api": True,
            "database": True
        },
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "version": "2.0.0"
    }

@app.post("/api/create-checkout-session")
async def create_checkout_session(request: Request, authorized: bool = Depends(verify_api_key)):
    """Create Stripe checkout session for book generation"""
    try:
        data = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    topic = data.get("topic", "Custom Book Project").strip()
    tier = validate_tier(data.get("tier", "pro"))
    
    if not topic or len(topic) > 200:
        raise HTTPException(status_code=400, detail="Invalid topic provided")
    
    price_id = STRIPE_PRODUCTS[tier]["price_id"]
    
    if not price_id or "price_" not in price_id:
        raise HTTPException(
            status_code=500, 
            detail="Payment system not configured properly"
        )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
                "adjustable_quantity": {"enabled": False}
            }],
            mode="payment",
            success_url=f"https://wizbook.io/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url="https://wizbook.io/cancel",
            customer_creation="always",
            metadata={
                "topic": topic[:100],
                "tier": tier,
                "project_id": datetime.now().strftime("%Y%m%d%H%M%S")
            },
            allow_promotion_codes=True,
            billing_address_collection="required",
            shipping_address_collection={"allowed_countries": ["US", "CA"]},
            phone_number_collection={"enabled": True}
        )
        
        logger.info(f"💰 Checkout session created for {tier} tier: {session.id}")
        
        return JSONResponse(status_code=200, content={
            "status": "success",
            "checkout_url": session.url,
            "session_id": session.id,
            "expires_at": session.expires_at
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
                "currency": "usd"
            }
            for tier, info in STRIPE_PRODUCTS.items()
        }
    }

# =========================
# 6️⃣ STATIC FILES (FALLBACK)
# =========================
# Serve static files if they exist (for frontend)
static_dir = "static"
if os.path.exists(static_dir) and os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    logger.info(f"📁 Serving static files from: {static_dir}")
else:
    logger.warning("⚠️ Static directory not found - API mode only")

# =========================
# 7️⃣ ERROR HANDLERS
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

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )

# =========================
# 8️⃣ PERFORMANCE MIDDLEWARE
# =========================
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response
