from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai
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
openai.api_key = os.getenv("OPENAI_API_KEY")

# Request/Response models


class Message(BaseModel):
    role: str  # "user", "assistant"
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
        # Convert messages to OpenAI format
        messages = [{"role": msg.role, "content": msg.content}
                    for msg in request.messages]

        # Call LLM API
        response = openai.ChatCompletion.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return ChatResponse(
            response=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        )

    except openai.error.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid API key")
    except openai.error.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except openai.error.APIError as e:
        raise HTTPException(
            status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")

# chat endpoint


@app.post("/chat")
async def simple_chat(message: str, model: Optional[str] = "gpt-3.5-turbo"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            temperature=0.7,
            max_tokens=500
        )

        return {
            "response": response.choices[0].message.content,
            "model": response.model
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
