from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# AI Book Models
class BookRequest(BaseModel):
    topic: str = Field(..., description="Main topic of the book")
    audience: str = Field(..., description="Target audience (e.g., 'beginners', 'professionals')")
    style: str = Field(default="professional", description="Writing style (academic/casual/storytelling)")
    length: str = Field(default="medium", description="Book length (short/medium/long)")
    tier: str = Field(default="pro", description="Payment tier (basic/pro/premium)")
    email: Optional[str] = Field(None, description="Customer email for delivery")

class BookResponse(BaseModel):
    id: str
    topic: str
    audience: str
    content: str
    status: str
    tier: str
    word_count: int
    created_at: datetime

class BookOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    book_request: BookRequest
    content: str
    status: str = "generated"
    word_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
# AI Book Generation Service
class AIBookGenerator:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def generate_book(self, request: BookRequest) -> str:
        """Generate a book using Emergent LLM with intelligent model selection"""
        
        # Define prompts based on tier and content type
        word_counts = {
            "basic": "5,000-8,000 words",
            "pro": "10,000-15,000 words", 
            "premium": "20,000-30,000 words"
        }
        
        # Create specialized prompt based on book characteristics
        if "technical" in request.topic.lower() or "programming" in request.topic.lower():
            # Use GPT-4 for technical content
            model_provider = "openai"
            model_name = "gpt-4o-mini"
            style_instruction = "technical yet accessible"
        elif "story" in request.topic.lower() or "creative" in request.topic.lower():
            # Use Claude for creative content
            model_provider = "anthropic"
            model_name = "claude-3-5-sonnet-20241022"
            style_instruction = "engaging and narrative-driven"
        else:
            # Use OpenAI for general content (more reliable)
            model_provider = "openai"
            model_name = "gpt-4o-mini"
            style_instruction = "clear and informative"

        system_message = f"""You are an expert book author specializing in creating high-quality, comprehensive books. 
        Generate a complete book that readers will find valuable enough to pay for.
        
        Style: {style_instruction}
        Target Audience: {request.audience}
        Expected Length: {word_counts.get(request.tier, '10,000-15,000 words')}
        """

        # Detailed book generation prompt
        user_prompt = f"""
        Create a comprehensive book about "{request.topic}" for {request.audience}.
        
        Requirements:
        - Title: Create an engaging, marketable title
        - Structure: 6-8 chapters with clear progression
        - Content: Practical, actionable information
        - Style: {request.style} writing style
        - Audience: Written specifically for {request.audience}
        - Length: Aim for {word_counts.get(request.tier, '10,000-15,000 words')}
        
        Format the book in clean Markdown with:
        - # Main Title
        - ## Chapter Titles
        - ### Section Headers
        - **Bold** for emphasis
        - `Code blocks` if applicable
        - > Blockquotes for key insights
        - 💡 **Pro Tip:** callouts throughout
        - ⚡ **Quick Win:** actionable items
        - 🔍 **Deep Dive:** advanced concepts
        
        Make this a book people would actually want to buy and read. Include:
        1. Practical examples
        2. Step-by-step instructions
        3. Common mistakes to avoid
        4. Advanced tips and tricks
        5. Real-world applications
        
        Start writing the complete book now:
        """

        # Try multiple approaches with proper error handling
        for attempt in range(3):
            try:
                logging.info(f"Attempt {attempt + 1}: Generating book with {model_provider}/{model_name}")
                
                # Initialize chat with appropriate model
                chat = LlmChat(
                    api_key=self.api_key,
                    session_id=f"book-gen-{uuid.uuid4()}-{attempt}",
                    system_message=system_message
                ).with_model(model_provider, model_name)
                
                # Generate the book
                user_message = UserMessage(text=user_prompt)
                response = await chat.send_message(user_message)
                
                if response and len(response.strip()) > 500:  # Validate response quality
                    logging.info(f"Successfully generated book with {len(response)} characters")
                    return response
                else:
                    logging.warning(f"Generated response too short: {len(response) if response else 0} characters")
                    
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < 2:  # Try different model on retry
                    model_provider = "openai"
                    model_name = "gpt-4o-mini"
                continue
        
        # All attempts failed, use enhanced fallback
        logging.warning("All AI generation attempts failed, using enhanced fallback")
        return self._generate_enhanced_fallback_book(request)
    
    def _generate_fallback_book(self, request: BookRequest) -> str:
        """Fallback book generation if AI fails"""
        return f"""# {request.topic} for {request.audience}

## Table of Contents
1. Introduction to {request.topic}
2. Getting Started
3. Core Concepts
4. Practical Applications
5. Advanced Techniques
6. Common Mistakes to Avoid
7. Best Practices
8. Next Steps

## Chapter 1: Introduction to {request.topic}

Welcome to your journey into {request.topic}! This book is specifically designed for {request.audience} who want to master this subject.

💡 **Pro Tip:** The key to learning {request.topic} is consistent practice and application.

### Why {request.topic} Matters

In today's world, understanding {request.topic} can give you a significant advantage...

[Content continues with structured chapters, examples, and practical advice]

## Chapter 2: Getting Started

⚡ **Quick Win:** Start with these three fundamental concepts...

[Book continues with comprehensive content]

---
*Generated by AI Book Generator - Premium Quality Content*
"""

# Initialize AI service
ai_generator = AIBookGenerator()

# API Routes
@api_router.get("/")
async def root():
    return {"message": "AI Book Generator API", "status": "active"}

@api_router.post("/generate-book", response_model=BookResponse)
async def generate_book(request: BookRequest):
    """Generate an AI-powered book based on user requirements"""
    try:
        # Generate book content using AI
        content = await ai_generator.generate_book(request)
        
        # Count words (rough estimate)
        word_count = len(content.split())
        
        # Create book order
        book_order = BookOrder(
            book_request=request,
            content=content,
            word_count=word_count
        )
        
        # Store in database
        await db.book_orders.insert_one(book_order.dict())
        
        # Return response
        return BookResponse(
            id=book_order.id,
            topic=request.topic,
            audience=request.audience,
            content=content,
            status="completed",
            tier=request.tier,
            word_count=word_count,
            created_at=book_order.created_at
        )
        
    except Exception as e:
        logging.error(f"Book generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Book generation failed: {str(e)}")

@api_router.get("/book/{book_id}")
async def get_book(book_id: str):
    """Retrieve a generated book by ID"""
    book = await db.book_orders.find_one({"id": book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@api_router.get("/books")
async def list_books(limit: int = 10):
    """List recent books (for admin/demo purposes)"""
    books = await db.book_orders.find().sort("created_at", -1).limit(limit).to_list(length=None)
    return {"books": books, "count": len(books)}

# Pricing tiers endpoint
@api_router.get("/pricing")
async def get_pricing():
    """Get available pricing tiers"""
    return {
        "tiers": [
            {
                "id": "basic",
                "name": "Basic Book",
                "price": 4.99,
                "description": "5-8k words, standard formatting",
                "features": ["AI-generated content", "PDF download", "Email delivery"]
            },
            {
                "id": "pro", 
                "name": "Pro Book",
                "price": 9.99,
                "description": "10-15k words, enhanced formatting",
                "features": ["AI-generated content", "Premium styling", "Multiple formats", "Priority support"],
                "recommended": True
            },
            {
                "id": "premium",
                "name": "Premium Book", 
                "price": 19.99,
                "description": "20-30k words, white-label ready",
                "features": ["Extended content", "White-label rights", "Source files", "Commercial license"]
            }
        ]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()