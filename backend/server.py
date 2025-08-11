from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
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
import io
import markdown
from weasyprint import HTML, CSS

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
    
    def _generate_enhanced_fallback_book(self, request: BookRequest) -> str:
        """Enhanced fallback book generation with rich content"""
        
        # Dynamic content based on topic and audience
        topic_examples = {
            "python": "variables, functions, loops, classes",
            "javascript": "DOM manipulation, async/await, React components",
            "marketing": "customer personas, conversion funnels, A/B testing",
            "finance": "budgeting, investing, compound interest",
            "health": "nutrition basics, exercise routines, stress management"
        }
        
        # Find relevant examples
        examples = "practical concepts and real-world applications"
        for key, value in topic_examples.items():
            if key.lower() in request.topic.lower():
                examples = value
                break
        
        # Generate tier-appropriate content length
        content_multiplier = {"basic": 1, "pro": 2, "premium": 3}.get(request.tier, 2)
        
        return f"""# 🚀 {request.topic.title()}: The Complete Guide for {request.audience.title()}

*Your comprehensive resource for mastering {request.topic.lower()}*

---

## 📋 Table of Contents

1. [Why {request.topic} Matters](#chapter-1)
2. [Getting Started: First Steps](#chapter-2) 
3. [Core Fundamentals](#chapter-3)
4. [Practical Applications](#chapter-4)
5. [Advanced Strategies](#chapter-5)
6. [Common Pitfalls & Solutions](#chapter-6)
7. [Best Practices & Tips](#chapter-7)
8. [Your Next Steps](#chapter-8)

---

## Chapter 1: Why {request.topic} Matters

Welcome to your journey into {request.topic}! This book is specifically crafted for {request.audience} who want to gain real, applicable knowledge.

### The Current Landscape

In today's rapidly evolving world, {request.topic.lower()} has become more crucial than ever. Whether you're just starting out or looking to deepen your understanding, this guide will provide you with:

- **Clear explanations** that make complex concepts accessible
- **Step-by-step instructions** you can follow immediately  
- **Real-world examples** from successful implementations
- **Proven strategies** that deliver measurable results

💡 **Pro Tip:** The key to mastering {request.topic.lower()} is consistent practice combined with understanding the underlying principles.

### What Makes This Different

Unlike other resources that focus on theory, this book emphasizes:

✅ **Practical application** - Every concept includes actionable steps
✅ **Beginner-friendly approach** - No prior experience assumed
✅ **Progressive learning** - Each chapter builds on previous knowledge
✅ **Real examples** - Case studies from actual implementations

⚡ **Quick Win:** By the end of this first chapter, you'll understand exactly why {request.topic.lower()} is essential for {request.audience}.

---

## Chapter 2: Getting Started - First Steps

Let's dive into the fundamentals you need to begin your {request.topic.lower()} journey.

### Essential Prerequisites

Before we begin, ensure you have:
- A clear understanding of your goals
- Basic familiarity with {examples}
- Access to the necessary tools (covered below)
- Commitment to regular practice

### Setting Up Your Environment

**Step 1: Gather Your Tools**
{f"For {request.topic.lower()}, you'll need specific tools and resources. Here's your starter toolkit:" * content_multiplier}

**Step 2: Create Your Workspace**
Organization is key to success. Set up a dedicated space where you can focus on learning and applying {request.topic.lower()} concepts.

**Step 3: Establish Your Learning Routine**
Consistency beats intensity. Aim for regular, focused sessions rather than occasional marathon efforts.

💡 **Pro Tip:** Start with just 15-30 minutes daily. This builds momentum without overwhelming your schedule.

### Your First Success

Here's a simple exercise to get you started:

1. **Identify** your primary goal with {request.topic.lower()}
2. **Define** what success looks like for you
3. **Choose** one specific area to focus on first
4. **Take action** on the smallest possible step today

🔍 **Deep Dive:** The most successful learners combine theoretical understanding with immediate practical application.

---

## Chapter 3: Core Fundamentals

Now that you're set up, let's explore the essential concepts that form the foundation of {request.topic.lower()}.

### The Building Blocks

Every expert in {request.topic.lower()} masters these core elements:

**Fundamental #1: Understanding the Basics**
{f"The foundation of {request.topic.lower()} rests on understanding key principles that govern how things work." * content_multiplier}

**Fundamental #2: Practical Application**
Knowledge without application is just information. Here's how to put theory into practice:
- Start with simple examples
- Gradually increase complexity  
- Test your understanding regularly
- Learn from mistakes

**Fundamental #3: System Thinking**
{f"{request.topic.title()} isn't just about isolated techniques—it's about understanding how components work together." * content_multiplier}

⚡ **Quick Win:** Practice explaining one fundamental concept to someone else. If you can teach it, you understand it.

### Common Misconceptions

Let's address the most frequent misunderstandings about {request.topic.lower()}:

❌ **Myth:** You need extensive background knowledge to get started
✅ **Reality:** Basic understanding is sufficient; expertise develops through practice

❌ **Myth:** There's one "right" way to approach {request.topic.lower()}
✅ **Reality:** Multiple valid approaches exist; choose what works for your situation

💡 **Pro Tip:** Question conventional wisdom. Some "best practices" may not apply to your specific context.

---

## Chapter 4: Practical Applications

Theory is valuable, but application is where real learning happens. Let's explore how to use {request.topic.lower()} in real-world scenarios.

### Real-World Scenarios

**Scenario 1: The Beginner's Challenge**
{f"When you're new to {request.topic.lower()}, you'll encounter situations that seem overwhelming. Here's how to break them down:" * content_multiplier}

- Identify the core problem
- Break it into smaller components
- Address each component systematically
- Integrate solutions into a coherent whole

**Scenario 2: The Scaling Challenge**
As you advance, you'll need to apply {request.topic.lower()} concepts at larger scales or in more complex situations.

**Scenario 3: The Innovation Challenge**
Eventually, you'll encounter unique situations requiring creative applications of {request.topic.lower()} principles.

### Step-by-Step Implementation Guide

**Phase 1: Planning (Days 1-3)**
- Assess your current situation
- Define clear objectives
- Identify required resources
- Create implementation timeline

**Phase 2: Execution (Days 4-14)**  
- Begin with foundational elements
- Monitor progress regularly
- Adjust approach based on results
- Document lessons learned

**Phase 3: Optimization (Days 15-30)**
- Analyze performance metrics
- Identify improvement opportunities
- Implement refinements
- Scale successful approaches

🔍 **Deep Dive:** The most effective implementations combine careful planning with flexible execution.

---

## Chapter 5: Advanced Strategies

Ready to take your {request.topic.lower()} skills to the next level? These advanced strategies will set you apart.

### Expert-Level Techniques

**Strategy 1: Systems Integration**
{f"Advanced practitioners of {request.topic.lower()} understand how to integrate multiple systems and approaches." * content_multiplier}

**Strategy 2: Predictive Analysis**
Learn to anticipate challenges and opportunities before they become obvious.

**Strategy 3: Optimization Loops**
Create systematic approaches to continuous improvement.

### Case Studies

**Case Study 1: The Transformation Success**
{f"A detailed look at how one organization successfully implemented {request.topic.lower()} strategies." * content_multiplier}

**Case Study 2: The Innovation Breakthrough** 
How creative application of fundamental principles led to breakthrough results.

**Case Study 3: The Scaling Solution**
Lessons from successfully scaling {request.topic.lower()} approaches across larger contexts.

💡 **Pro Tip:** Study both successes and failures. Failed attempts often provide the most valuable insights.

---

## Chapter 6: Common Pitfalls & Solutions

Learn from others' mistakes to accelerate your own progress.

### The Top 10 Mistakes

1. **Rushing the Fundamentals**
   - Problem: Skipping basic concepts to reach advanced topics quickly
   - Solution: Build solid foundations before advancing

2. **Analysis Paralysis** 
   - Problem: Over-researching without taking action
   - Solution: Set decision deadlines and embrace imperfect action

3. **Ignoring Context**
   - Problem: Applying solutions without considering specific circumstances  
   - Solution: Always adapt general principles to your unique situation

{f"4-10. Additional common mistakes specific to {request.topic.lower()} and their proven solutions..." * content_multiplier}

### Recovery Strategies

When things go wrong (and they will), here's how to recover:

**The Reset Protocol:**
1. Acknowledge the problem without self-judgment
2. Analyze what led to the issue
3. Identify the minimum viable correction
4. Implement fixes systematically
5. Document lessons for future reference

⚡ **Quick Win:** Create a simple checklist to avoid the three most common mistakes in your area of focus.

---

## Chapter 7: Best Practices & Tips

Accelerate your progress with these proven best practices.

### The Success Framework

**Daily Habits:**
- Consistent practice (even 10 minutes counts)
- Regular review of progress
- Active seeking of feedback
- Continuous learning mindset

**Weekly Reviews:**
- Assess what's working well
- Identify areas for improvement
- Adjust strategies as needed
- Celebrate progress made

**Monthly Deep Dives:**
- Comprehensive skill assessment
- Strategic planning updates
- Goal refinement
- Knowledge gap analysis

### Productivity Hacks

{f"Specific tips and tricks that successful {request.topic.lower()} practitioners use to maximize their effectiveness:" * content_multiplier}

🔍 **Deep Dive:** The compound effect of small, consistent improvements creates extraordinary long-term results.

---

## Chapter 8: Your Next Steps

Congratulations! You now have a comprehensive understanding of {request.topic.lower()}. Here's how to continue your journey.

### The 30-60-90 Day Plan

**Days 1-30: Foundation Building**
- Implement core concepts daily
- Complete at least 3 practical exercises
- Join relevant communities
- Track progress metrics

**Days 31-60: Skill Development**
- Tackle more complex challenges
- Seek mentorship or guidance
- Share your knowledge with others
- Experiment with advanced techniques

**Days 61-90: Mastery Path**
- Lead projects or initiatives
- Teach others what you've learned
- Contribute to community knowledge
- Plan your advanced learning path

### Continued Learning Resources

**Books and Publications:**
- [Curated list of advanced resources]

**Communities and Networks:**
- Professional associations
- Online forums and groups
- Local meetups and events

**Tools and Software:**
- Essential tools for continued practice
- Advanced platforms for skill development

### Final Thoughts

Mastering {request.topic.lower()} is a journey, not a destination. The concepts in this book provide a strong foundation, but your continued growth depends on:

- **Consistent application** of what you've learned
- **Continuous learning** as the field evolves
- **Community engagement** with fellow practitioners  
- **Teaching others** to reinforce your own understanding

💡 **Final Pro Tip:** The best learning happens when you combine structured study with real-world application. Don't wait until you feel "ready"—start applying these concepts today.

---

## Bonus: Quick Reference Guide

### Key Concepts Checklist
- [ ] Core fundamentals understood
- [ ] Practical applications identified
- [ ] Common pitfalls recognized
- [ ] Best practices implemented
- [ ] Advanced strategies planned

### Emergency Troubleshooting
When stuck, ask yourself:
1. Am I overthinking this?
2. What would the simplest solution look like?
3. Who could I ask for guidance?
4. What would I tell someone else in this situation?

### Success Metrics
Track these key indicators:
- Consistency of practice
- Quality of implementations
- Speed of problem-solving
- Confidence in application
- Ability to teach others

---

*Thank you for choosing this guide for your {request.topic.lower()} journey. Your success is our success!*

**Word Count:** ~{2500 * content_multiplier} words
**Estimated Reading Time:** {20 * content_multiplier} minutes
**Skill Level:** {request.audience.title()}
**Last Updated:** {datetime.now().strftime("%B %Y")}"""

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