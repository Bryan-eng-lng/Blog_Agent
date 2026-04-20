import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from agent import plan_blog, research, write_blog, critique_and_rewrite, generate_seo, fix_cliches, score_blog, analyze_competitor_gap, generate_extras
from memory import store_memory, retrieve_memory

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

    topic = request.topic
    audience = request.audience
    length = request.length

    # Step 1: Plan (includes competitor gap analysis)
    plan = plan_blog(topic, audience)
    time.sleep(3)

    # Step 2: Research
    research_data = research(topic)
    time.sleep(3)

    # Step 3: Retrieve memory
    memory = retrieve_memory(topic)

    # Step 4: Write first draft
    draft = write_blog(topic, audience, plan, research_data, memory, length=length, gap="")

    # Step 5: Critique and rewrite
    final_blog = critique_and_rewrite(draft, topic, audience)
    time.sleep(3)

    # Step 7: Remove cliches
    final_blog = fix_cliches(final_blog, topic)

    # Step 8: Generate SEO, extras and score in one call
    seo = generate_seo(topic, final_blog)
    time.sleep(3)
    extras = generate_extras(final_blog, topic)
    time.sleep(3)
    scores = score_blog(final_blog, topic, seo)

    # Step 10: Store to memory
    store_memory(topic)
    store_memory(final_blog)

    return {
        "topic": topic,
        "audience": audience,
        "plan": plan,
        "draft": draft,
        "final_blog": final_blog,
        "extras": extras,
        "seo": seo,
        "scores": scores
    }
