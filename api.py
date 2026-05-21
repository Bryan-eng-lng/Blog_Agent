import os
import time
import logging
import sentry_sdk
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from graph import run_blog_pipeline

# ── Sentry setup ──────────────────────────────────────────────────────────────
_sentry_dsn = os.getenv("SENTRY_DSN", "")
sentry_sdk.init(
    dsn=_sentry_dsn,
    traces_sample_rate=0.1,
    environment="production",
    send_default_pii=False
)
if _sentry_dsn:
    print("✅ Sentry initialized successfully")
else:
    print("⚠️  SENTRY_DSN not set — Sentry is disabled")

# ── Logging setup ─────────────────────────────────────────────────────────────
log_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("blog_api")
logger.setLevel(logging.INFO)

# Console handler — shows in terminal and Render logs
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# File handler — saves to blog_api.log locally
file_handler = logging.FileHandler("blog_api.log")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

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
    start = time.time()
    logger.info(f"[REQUEST] topic='{request.topic[:60]}' | audience='{request.audience[:40]}' | length={request.length}")
    try:
        result = run_blog_pipeline(
            topic=request.topic,
            audience=request.audience or "general readers",
            length=request.length or "medium",
        )
        duration = time.time() - start
        word_count = len(result.get("final_blog", "").split())
        score = result.get("scores", {}).get("Overall Score", "N/A")
        logger.info(f"[SUCCESS] topic='{request.topic[:60]}' | duration={duration:.1f}s | words={word_count} | score={score}")
        return result
    except Exception as e:
        duration = time.time() - start
        msg = str(e).lower()
        logger.error(f"[FAILED] topic='{request.topic[:60]}' | duration={duration:.1f}s | error={str(e)[:120]}")
        if "rate limit" in msg or "rate limited" in msg or "429" in msg:
            raise HTTPException(
                status_code=429,
                detail="API rate limit reached. Please try again in 5 minutes."
            )
        sentry_sdk.capture_exception(e)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )


