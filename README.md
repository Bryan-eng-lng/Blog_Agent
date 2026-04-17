# Blog Writer Agent

A research-first blog writing agent that produces deeply researched, publish-ready blog posts using a multi-step agentic pipeline.

Unlike a single LLM call, this agent plans, researches, extracts facts, analyzes competitors, writes, critiques, rewrites, removes clichés, scores, and generates SEO metadata — all automatically.

---

## Pipeline

1. Plan — generates a specific, audience-aware blog outline with recommended length
2. Competitor Gap Analysis — finds what existing articles miss and writes to fill that gap
3. Research — runs 4 parallel web searches using Tavily
4. Memory Retrieval — pulls relevant past context from vector memory (Chroma)
5. Fact Extraction — strips raw research down to named sources, real stats, and concrete examples
6. Write Draft — writes a full blog using only verified facts
7. Critique and Rewrite — a senior editor pass that fixes weak hooks, filler, and poor conclusions
8. Cliché Detection — scans for 30+ known clichés and replaces them with topic-specific language
9. SEO Metadata — generates meta title, description, keywords, tags, and read time
10. Extras — generates TL;DR, pull quote, and key takeaway
11. Blog Score — scores the final blog across readability, hook strength, depth, SEO, and conclusion quality

---

## Tech Stack

- LLM: Groq (llama-3.3-70b-versatile) with automatic key rotation
- Search: Tavily API (advanced depth, parallel queries)
- Memory: Chroma + HuggingFace embeddings (all-MiniLM-L6-v2, no server required)
- Framework: LangChain + FastAPI

---

## Setup

1. Clone the repo and install dependencies

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the `blog_agent` folder

```
TAVILY_API_KEY=your_tavily_key
GROQ_KEY_1=your_first_groq_key
GROQ_KEY_2=your_second_groq_key
```

3. Run the CLI

```bash
python main.py
```

Or start the API server

```bash
uvicorn api:app --reload
```

No Ollama required. Embeddings run locally via HuggingFace.

---

## Dry Run Mode

After entering a topic and audience, the agent shows the blog plan and competitor gap analysis before spending any tokens on writing. You can review and cancel if the angle isn't right.

```
Enter blog topic: Why Most Diets Fail in the First 30 Days
Target audience: People aged 25-40 who keep falling off track

Step 1 — Planning the blog...
[outline appears]

Step 2 — Analyzing competitor gap...
Most articles focus on willpower. None address the hormonal response to restriction.

Dry run preview done. Continue with full blog? (y/n): 
```

---

## API Usage

POST `/generate-blog`

```json
{
  "topic": "Why Most Diets Fail in the First 30 Days",
  "audience": "People aged 25-40 who keep falling off track",
  "length": "medium"
}
```

Length options: `short` (600-800 words), `medium` (1000-1500 words), `long` (2000-2500 words)

Response includes: `plan`, `draft`, `final_blog`, `extras` (TL;DR, pull quote, key takeaway), `seo`, `scores`

---

## Example Output

Topic: "Why Your Morning Coffee Is More Expensive Than It Was 2 Years Ago"
Target Audience: Coffee drinkers aged 22-40

**Competitor Gap Analysis:**
> Most articles blame inflation generically. None explain the role of middlemen and commodity traders in amplifying price spikes beyond what climate alone would cause.

**TL;DR:**
- Ground roast coffee hit $8.41/lb in July 2025 — a 33% increase from a year ago
- Climate change in Brazil reduced crop yields, but commodity traders amplified the spike
- Specialty coffee demand is shifting costs upstream to farmers and consumers simultaneously

**Pull Quote:**
> "Free shipping isn't really free for any of us — the cost will have to get swallowed somewhere."

**Blog Score:**
- Readability: 8 — Short paragraphs, clear language
- Hook Strength: 9 — Opens with a specific dated stat
- Content Depth: 8 — Named sources and real data throughout
- SEO Strength: 7 — Focus keyword used naturally
- Conclusion Quality: 8 — Ends with a specific, memorable line
- Overall Score: 8.0
- Verdict: Strong research and structure, conclusion could be sharper

---

## What Makes It Different

Most AI blog tools make a single LLM call. This agent:

- Searches the web before writing — no hallucinated statistics
- Analyzes what competitors have already written and fills the gap
- Runs a dedicated fact extraction step so the writer only uses verified data
- Has a built-in editor that rewrites weak sections
- Detects and replaces 30+ clichés automatically
- Scores its own output so users know what they're publishing
- Dry run mode lets users review the plan before committing

---

## Project Structure

```
blog_agent/
├── agent.py       # Core pipeline — all LLM functions
├── tools.py       # Tavily web search
├── memory.py      # Chroma vector store with HuggingFace embeddings
├── main.py        # CLI interface with dry-run mode
├── api.py         # FastAPI endpoint
└── .env           # API keys (not committed)
```
