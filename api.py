from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from agent import plan_blog, research, write_blog, critique_and_rewrite, generate_seo, fix_cliches, score_blog, analyze_competitor_gap, generate_extras
from memory import store_memory, retrieve_memory

app = FastAPI(title="Blog Writer Agent")


class BlogRequest(BaseModel):
    topic: str
    audience: Optional[str] = "general readers"
    length: Optional[str] = "medium"


@app.post("/generate-blog")
def generate_blog(request: BlogRequest):

    topic = request.topic
    audience = request.audience
    length = request.length

    # Step 1: Plan
    plan = plan_blog(topic, audience)

    # Step 2: Research
    research_data = research(topic)

    # Step 3: Competitor gap analysis
    gap = analyze_competitor_gap(topic)

    # Step 4: Retrieve memory
    memory = retrieve_memory(topic)

    # Step 5: Write first draft
    draft = write_blog(topic, audience, plan, research_data, memory, length=length, gap=gap)

    # Step 6: Critique and rewrite
    final_blog = critique_and_rewrite(draft, topic, audience)

    # Step 7: Remove cliches
    final_blog = fix_cliches(final_blog, topic)

    # Step 8: Generate SEO metadata
    seo = generate_seo(topic, final_blog)

    # Step 9: Score the blog
    scores = score_blog(final_blog, topic, seo)

    # Step 9: Generate extras
    extras = generate_extras(final_blog, topic)

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
