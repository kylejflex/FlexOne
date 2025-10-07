from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Literal
from openai import OpenAI
from openai import (
    AuthenticationError,
    RateLimitError,
    APIStatusError,
    APIConnectionError,
    BadRequestError
)
import os
import json
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError(
        "OPENAI_API_KEY environment variable is not set. "
        "Please copy .env.example to .env and add your API key."
    )

app = FastAPI(title="FlexOne API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load knowledge base from doc.json
KNOWLEDGE_BASE = {}
KB_LOADED = False


def load_knowledge_base():
    """Load the knowledge base from doc.json file."""
    global KNOWLEDGE_BASE, KB_LOADED
    try:
        with open("doc.json", "r", encoding="utf-8") as f:
            KNOWLEDGE_BASE = json.load(f)
            KB_LOADED = True
            print("✅ Knowledge base loaded successfully from doc.json")
    except FileNotFoundError:
        print(
            "⚠️ Warning: doc.json not found. AI will work without knowledge base context.")
        KB_LOADED = False
    except json.JSONDecodeError as e:
        print(f"⚠️ Warning: Error parsing doc.json: {e}")
        KB_LOADED = False


# Load knowledge base on startup
load_knowledge_base()


def create_system_prompt() -> str:
    """Create a system prompt that includes the knowledge base context."""
    base_prompt = """You are FlexOne AI Assistant, an intelligent guide for Consumer Edge testing and operations.

Your personality:
- Friendly, helpful, and professional
- Use emojis sparingly (👋 ✅ 🔹 ⚠️) to make responses engaging
- Break down complex topics into digestible steps
- Proactive in offering additional help
- Clear and concise

Response Guidelines:
1. **Detect Intent**: Understand if the user needs:
   - Tutorial/Step-by-step guidance
   - Quick information
   - Commands/technical reference
   - Troubleshooting help

2. **Response Style**:
   - For beginners: Explain concepts first, then provide commands
   - For experienced users: Give direct answers with commands
   - Always offer to elaborate or show related information
   
3. **Structure Your Responses**:
   - Start with a brief acknowledgment
   - Provide the core answer
   - Offer next steps or related help
   - Use markdown formatting for readability

4. **Command Formatting**:
   - Always use code blocks for commands
   - Explain what each command does
   - Show expected output when relevant

5. **Proactive Assistance**:
   - Suggest related topics
   - Offer deeper dives into subjects
   - Ask clarifying questions when needed

Remember: You're here to make testing and operations easier for the team. Be supportive and informative!"""

    if KB_LOADED and KNOWLEDGE_BASE:
        base_prompt += f"\n\nKnowledge Base Context:\n{json.dumps(KNOWLEDGE_BASE, indent=2)}"

    return base_prompt


# Request/Response models
class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1500
    use_knowledge_base: Optional[bool] = True


class ChatResponse(BaseModel):
    response: str
    model: str
    usage: dict
    knowledge_base_used: bool


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "FlexOne API",
        "version": "1.0.0",
        "knowledge_base_loaded": KB_LOADED,
        "endpoints": {
            "/chat": "POST - Main chat endpoint (used by Streamlit frontend, includes KB)",
            "/chat/simple": "POST - Simple single-message chat",
            "/chat/kb": "POST - Chat with knowledge base context (alternative)",
            "/chat/details": "POST - Detailed chat with full control",
            "/health": "GET - Check API health",
            "/knowledge-base": "GET - View knowledge base info",
            "/knowledge-base/category/{name}": "GET - Get specific category",
            "/knowledge-base/reload": "POST - Reload knowledge base from doc.json"
        }
    }


# Health check endpoint
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "knowledge_base_loaded": KB_LOADED
    }


# Knowledge base info endpoint
@app.get("/knowledge-base")
async def get_knowledge_base_info():
    """Get information about the loaded knowledge base."""
    if not KB_LOADED:
        return {
            "loaded": False,
            "message": "Knowledge base not loaded. Please ensure doc.json exists."
        }

    kb_data = KNOWLEDGE_BASE.get("knowledge_base", {})
    categories = list(kb_data.get("categories", {}).keys())
    quick_ref = kb_data.get("quick_reference", {})

    return {
        "loaded": True,
        "product_name": kb_data.get("product_name", "Unknown"),
        "version": kb_data.get("version", "Unknown"),
        "last_updated": kb_data.get("last_updated", "Unknown"),
        "categories": categories,
        "common_queries": quick_ref.get("common_queries", [])
    }


# Reload knowledge base endpoint
@app.post("/knowledge-base/reload")
async def reload_knowledge_base():
    """Reload the knowledge base from doc.json."""
    load_knowledge_base()
    return {
        "success": KB_LOADED,
        "message": "Knowledge base reloaded successfully" if KB_LOADED else "Failed to reload knowledge base"
    }


# Get specific category from knowledge base
@app.get("/knowledge-base/category/{category_name}")
async def get_category(category_name: str):
    """Get detailed information about a specific knowledge base category."""
    if not KB_LOADED:
        raise HTTPException(
            status_code=503,
            detail="Knowledge base not loaded"
        )

    categories = KNOWLEDGE_BASE.get("knowledge_base", {}).get("categories", {})

    if category_name not in categories:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category_name}' not found. Available: {list(categories.keys())}"
        )

    return {
        "category": category_name,
        "data": categories[category_name]
    }


# Chat endpoint with knowledge base
@app.post("/chat/kb")
async def chat_with_knowledge_base(
    message: str,
    model: Optional[str] = "gpt-3.5-turbo",
    temperature: Optional[float] = 0.7,
    max_tokens: Optional[int] = 1500
):
    """
    Simple chat endpoint that automatically includes knowledge base context.
    Use this for quick queries with full knowledge base support.
    """
    try:
        # Build messages with system prompt
        messages = [
            {"role": "system", "content": create_system_prompt()},
            {"role": "user", "content": message}
        ]

        response = client.chat.completions.create(
            model=(model or "gpt-3.5-turbo"),
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return {
            "response": response.choices[0].message.content or "",
            "model": response.model,
            "knowledge_base_used": KB_LOADED,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        }

    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid API key")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except APIConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Network error: {e}")
    except APIStatusError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}")


# Detailed chat endpoint with full control
@app.post("/chat/details", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Detailed chat endpoint with conversation history support.
    Optionally includes knowledge base context via use_knowledge_base parameter.
    """
    try:
        # Convert messages to OpenAI format
        messages = [{"role": msg.role, "content": msg.content}
                    for msg in request.messages]

        # Inject system prompt with knowledge base if requested
        if request.use_knowledge_base and KB_LOADED:
            # Check if there's already a system message
            has_system = any(msg["role"] == "system" for msg in messages)

            if not has_system:
                # Add system prompt at the beginning
                messages.insert(0, {
                    "role": "system",
                    "content": create_system_prompt()
                })
            else:
                # Enhance existing system message with KB context
                for msg in messages:
                    if msg["role"] == "system":
                        if KB_LOADED and KNOWLEDGE_BASE:
                            msg["content"] += f"\n\nKnowledge Base Context:\n{json.dumps(KNOWLEDGE_BASE, indent=2)}"
                        break

        # Call LLM API
        response = client.chat.completions.create(
            model=(request.model or "gpt-3.5-turbo"),
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        text = response.choices[0].message.content or ""
        model_used = response.model
        usage_obj = response.usage

        return ChatResponse(
            response=text,
            model=model_used,
            usage={
                "prompt_tokens": getattr(usage_obj, "prompt_tokens", None),
                "completion_tokens": getattr(usage_obj, "completion_tokens", None),
                "total_tokens": getattr(usage_obj, "total_tokens", None),
            },
            knowledge_base_used=request.use_knowledge_base and KB_LOADED
        )

    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid API key")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except APIConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Network error: {e}")
    except APIStatusError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}")


# Main chat endpoint for Streamlit frontend
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint that accepts conversation messages.
    This endpoint is used by the Streamlit frontend.
    Automatically includes knowledge base context if available.
    """
    try:
        # Convert messages to OpenAI format
        messages = [{"role": msg.role, "content": msg.content}
                    for msg in request.messages]

        # Always inject KB context if loaded (this is the primary use case)
        if KB_LOADED:
            # Check if there's already a system message
            has_system = any(msg["role"] == "system" for msg in messages)

            if not has_system:
                # Add system prompt at the beginning
                messages.insert(0, {
                    "role": "system",
                    "content": create_system_prompt()
                })

        # Call OpenAI API
        response = client.chat.completions.create(
            model=request.model or "gpt-3.5-turbo",
            messages=messages,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 1500,
        )

        return {
            "response": response.choices[0].message.content or "",
            "model": response.model,
            "knowledge_base_used": KB_LOADED,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        }

    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid API key")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except APIConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Network error: {e}")
    except APIStatusError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}")


# Simple chat endpoint (alternative - for quick testing)
@app.post("/chat/simple")
async def simple_chat(
    message: str,
    model: Optional[str] = "gpt-3.5-turbo",
    use_kb: Optional[bool] = True
):
    """
    Simple chat endpoint for quick testing. Set use_kb=false to exclude knowledge base.
    """
    try:
        messages = [{"role": "user", "content": message}]

        # Add knowledge base context if requested
        if use_kb and KB_LOADED:
            messages.insert(0, {
                "role": "system",
                "content": create_system_prompt()
            })

        response = client.chat.completions.create(
            model=(model or "gpt-3.5-turbo"),
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
        )

        return {
            "response": response.choices[0].message.content or "",
            "model": response.model,
            "knowledge_base_used": use_kb and KB_LOADED
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
