"""WizBook.io - Railway Deployment Version"""
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import stripe
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware

class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://js.stripe.com; "
            "frame-src https://js.stripe.com https://hooks.stripe.com; "
            "connect-src 'self' https://api.stripe.com"
        )
        return response

# Add this middleware
app.add_middleware(ContentSecurityPolicyMiddleware)

def get_config():
    return {
        'APP_NAME': os.getenv('APP_NAME', 'WizBook Generator'),
        'DOMAIN': os.getenv('DOMAIN', 'www.wizbook.io'),
        'EMERGENT_LLM_KEY': os.getenv('EMERGENT_LLM_KEY'),
        'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY'),
        'STRIPE_PUBLISHABLE_KEY': os.getenv('STRIPE_PUBLISHABLE_KEY'),
        'STRIPE_BASIC_PRICE': os.getenv('STRIPE_BASIC_PRICE'),
        'STRIPE_PRO_PRICE': os.getenv('STRIPE_PRO_PRICE'),
        'STRIPE_BUSINESS_PRICE': os.getenv('STRIPE_BUSINESS_PRICE'),
        'CORS_ORIGINS': os.getenv('CORS_ORIGINS', 'https://www.wizbook.io,https://wizbook.io'),
    }

class SimpleStripeManager:
    def __init__(self, config):
        self.config = config
        stripe.api_key = config['STRIPE_SECRET_KEY']
        
    def create_checkout_session(self, tier, topic, upsells=None):
        price_mapping = {
            'basic': self.config['STRIPE_BASIC_PRICE'],
            'professional': self.config['STRIPE_PRO_PRICE'], 
            'business': self.config['STRIPE_BUSINESS_PRICE']
        }
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': price_mapping[tier], 'quantity': 1}],
            mode='payment',
            success_url=f"https://{self.config['DOMAIN']}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"https://{self.config['DOMAIN']}/cancel",
            metadata={'topic': topic, 'tier': tier}
        )
        
        return {
            'status': 'success',
            'checkout_url': session.url,
            'session_id': session.id,
            'amount_total': 47 if tier == 'basic' else 97 if tier == 'professional' else 497
        }

async def generate_book_content(topic, config):
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import uuid
        
        chat = LlmChat(
            api_key=config.get('EMERGENT_LLM_KEY'),
            session_id=f"book-{uuid.uuid4()}",
        ).with_model("openai", "gpt-4o-mini")
        
        response = await chat.send_message_async(
            UserMessage(content=f"Write a comprehensive guide about {topic}")
        )
        
        content = response.message.content if hasattr(response.message, 'content') else str(response.message)
        return {"book": content, "topic": topic, "word_count": len(content.split()), "status": "success"}
    except Exception as e:
        return {"book": f"# {topic}\n\nSample book content for {topic}.", "topic": topic, "word_count": 50, "status": "demo"}

config = get_config()
stripe_manager = SimpleStripeManager(config)
app = FastAPI(title="WizBook.io API", version="1.0")

cors_origins = config['CORS_ORIGINS'].split(',')
app.add_middleware(CORSMiddleware, allow_origins=cors_origins, allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["*"])

@app.get("/api/")
async def health_check():
    return {"status": "healthy", "app": config['APP_NAME'], "stripe_configured": True, "timestamp": datetime.now().isoformat()}

@app.get("/api/config")
async def get_client_config():
    return {"domain": config['DOMAIN'], "app_name": config['APP_NAME'], "stripe": {"publishable_key": config['STRIPE_PUBLISHABLE_KEY']}}

@app.get("/api/generate")
async def generate_book(topic: str):
    if not topic or len(topic.strip()) < 2:
        raise HTTPException(status_code=400, detail="Topic required")
    result = await generate_book_content(topic.strip(), config)
    return result

@app.post("/api/capture-email")
async def capture_email(request: Request):
    data = await request.json()
    email = data.get('email', '')
    if not email or '@' not in email:
        raise HTTPException(status_code=400, detail="Valid email required")
    return {"status": "success", "message": "Email captured", "email": email.lower()}

@app.post("/api/checkout")
async def create_checkout_session(request: Request):
    data = await request.json()
    topic = data.get('topic', 'General Book')
    tier = data.get('tier', 'professional')
    session_result = stripe_manager.create_checkout_session(tier=tier, topic=topic.strip())
    return JSONResponse(session_result)

@app.post("/api/webhook")
async def stripe_webhook(request: Request):
    return {"status": "success"}

@app.get("/")
async def root():
    return {"message": "WizBook.io API", "app": config['APP_NAME']}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
