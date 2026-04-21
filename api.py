import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from graph import run_blog_pipeline

app = FastAPI(title="Blog Writer Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class BlogRequest(BaseModel):
    topic: str
    audience: Optional[str] = "general readers"
    length: Optional[str] = "medium"


@app.post("/generate-blog")
def generate_blog(request: BlogRequest):
    try:
        result = run_blog_pipeline(
            topic=request.topic,
            audience=request.audience or "general readers",
            length=request.length or "medium",
        )
        return result
    except Exception as e:
        msg = str(e).lower()
        if "rate limit" in msg or "rate limited" in msg or "429" in msg:
            raise HTTPException(
                status_code=429,
                detail="API rate limit reached. Please try again in 5 minutes."
            )
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )
