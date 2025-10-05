from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Literal
# import openai
# from openai.error import AuthenticationError, RateLimitError, APIError
from openai import OpenAI
from openai import (AuthenticationError, RateLimitError, APIStatusError, APIConnectionError, BadRequestError)
import os
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

# Set your OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Request/Response models
class Message(BaseModel):
    role: Literal["user", "assistant", "system"] # can change these later but needs to fit data types
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500


class ChatResponse(BaseModel):
    response: str
    model: str
    usage: dict

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "FlexOne API",
        "endpoints": {
            "/chat": "POST - Send messages and get LLM response",
            "/health": "GET - Check API health"
        }
    }

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}

# Chat endpoint
@app.post("/chat/details", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Convert messages to OpenAI format. Type implictly matches OpenAI schema, so the error below is silent and won't hit at runtime
        messages = [{"role": msg.role, "content": msg.content}for msg in request.messages]
        
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
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# chat endpoint
@app.post("/chat")
async def simple_chat(message: str, model: Optional[str] = "gpt-3.5-turbo"):
    try:
        response = client.chat.completions.create(
            model=(model or "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": message}],
            temperature=0.7,
            max_tokens=500,
        )

        return {
            "response": response.choices[0].message.content or "",
            "model": response.model,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
